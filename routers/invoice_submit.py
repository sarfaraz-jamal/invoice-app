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


router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)


@router.post("/submit")
async def submit_invoice_route(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Submit an invoice to FBR.

    Current responsibility:
        1. Read tenant_id from session
        2. Load tenant from database
        3. Read invoice JSON payload
        4. Submit invoice to FBR
        5. Return normalized FBR response

    Database persistence will be added after invoice_service.py
    is implemented.
    """

    # -----------------------------------------------------
    # 1. AUTH / TENANT
    # -----------------------------------------------------

    tenant_id = request.session.get("tenant_id")

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
    # 2. READ INVOICE PAYLOAD
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

    environment = payload.pop(
    "environment",
    "sandbox",
)
    # -----------------------------------------------------
    # 3. SUBMIT TO FBR
    # -----------------------------------------------------

    try:
        fbr_result = await submit_invoice(
        tenant=tenant,
        payload=payload,
        environment=environment,
    )

    except FBRSubmissionError as exc:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": exc.message,
                "fbr_error_code": exc.error_code,
                "fbr_http_status": exc.status_code,
                "fbr_response": exc.response,
            },
        )

    # -----------------------------------------------------
    # 4. SUCCESS
    # -----------------------------------------------------

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Invoice submitted successfully to FBR.",
            "invoice_number": fbr_result.invoice_number,
            "dated": fbr_result.dated,
            "status": fbr_result.status,
            "status_code": fbr_result.status_code,
            "item_statuses": fbr_result.item_statuses,
            "fbr_response": fbr_result.raw_response,
        },
    )