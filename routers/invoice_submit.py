import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from models.tenant import Tenant

from services.fbr_invoice_service import (
    FBRSubmissionError,
    submit_invoice,
)

from services.invoice_service import (
    create_invoice,
    mark_invoice_accepted,
    mark_invoice_failed,
)


router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)


@router.post("/submit")
async def submit_invoice_route(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):

    # -----------------------------------------------------
    # 1. AUTH / TENANT
    # -----------------------------------------------------

    tenant_id = request.session.get("tenant_id")
    user_id = request.session.get("user_id")

    if not tenant_id:
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message": "Tenant session not found.",
            },
        )

    try:
        tenant_uuid = uuid.UUID(str(tenant_id))
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Invalid tenant ID in session.",
            },
        )

    user_uuid = None

    if user_id:
        try:
            user_uuid = uuid.UUID(str(user_id))
        except ValueError:
            pass

    result = await db.execute(
        select(Tenant).where(
            Tenant.id == tenant_uuid,
            Tenant.is_active.is_(True),
        )
    )

    tenant = result.scalar_one_or_none()

    if not tenant:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": "Active tenant not found.",
            },
        )

    # -----------------------------------------------------
    # 2. READ PAYLOAD
    # -----------------------------------------------------

    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Invalid JSON invoice payload.",
            },
        )

    if not isinstance(payload, dict):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Invoice payload must be a JSON object.",
            },
        )

    # Make a copy because we don't want environment
    # included in the FBR payload.
    payload = payload.copy()

    environment = payload.pop(
        "environment",
        "sandbox",
    )

    invoice_number = payload.pop(
        "invoiceNumber",
        None,
            )

    if environment not in {
        "sandbox",
        "production",
    }:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Invalid FBR environment.",
            },
        )

    

    if not invoice_number:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Invoice number is required.",
            },
        )

    # -----------------------------------------------------
    # 3. SAVE LOCALLY FIRST
    # -----------------------------------------------------

    try:
        invoice = await create_invoice(
            db=db,
            tenant_id=tenant_uuid,
            user_id=user_uuid,
            payload=payload,
            environment=environment,
            invoice_number=invoice_number,
            
        )

    except Exception as exc:
        await db.rollback()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Could not save invoice locally.",
                "error": str(exc),
            },
        )

    # -----------------------------------------------------
    # 4. SUBMIT TO FBR
    # -----------------------------------------------------

    print("========== CLEAN FBR PAYLOAD ==========")
    print(payload)
    print("=======================================")

    try:
        fbr_result = await submit_invoice(
            tenant=tenant,
            payload=payload,
            environment=environment,
        )

    except FBRSubmissionError as exc:

        await mark_invoice_failed(
            db=db,
            invoice=invoice,
            error=exc,
        )

        return JSONResponse(
            status_code=422,
            content={
                "success": False,

                # Our invoice still exists
                "invoice_id": str(invoice.id),
                "invoice_number": invoice.invoice_number,

                "status": invoice.status,

                "message": exc.message,
                "fbr_error_code": exc.error_code,
                "fbr_http_status": exc.status_code,
                "fbr_response": exc.response,
            },
        )

    # -----------------------------------------------------
    # 5. SAVE FBR SUCCESS
    # -----------------------------------------------------

    await mark_invoice_accepted(
        db=db,
        invoice=invoice,
        fbr_result=fbr_result,
    )

    # -----------------------------------------------------
    # 6. RETURN SUCCESS
    # -----------------------------------------------------

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": (
                "Invoice submitted successfully to FBR."
            ),

            # Our invoice
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number,

            # FBR invoice
            "fbr_invoice_number": (
                fbr_result.invoice_number
            ),

            "dated": fbr_result.dated,
            "status": invoice.status,

            "fbr_status": fbr_result.status,
            "fbr_status_code": (
                fbr_result.status_code
            ),

            "item_statuses": (
                fbr_result.item_statuses
            ),

            "fbr_response": (
                fbr_result.raw_response
            ),
        },
    )