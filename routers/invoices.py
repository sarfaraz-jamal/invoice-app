import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.database import get_db
from models.invoice import Invoice

from datetime import date

import io
import qrcode

from fastapi.responses import StreamingResponse



router = APIRouter(
    tags=["Invoices"]
)

templates = Jinja2Templates(directory="templates")


@router.get("")
async def invoices_list(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    environment: str | None = None,
):
    tenant_id = request.session.get("tenant_id")

    tenant_uuid = uuid.UUID(str(tenant_id))

    query = (
        select(Invoice)
        .where(Invoice.tenant_id == tenant_uuid)
    )

    if environment in {"sandbox", "production"}:
        query = query.where(
            Invoice.fbr_environment == environment
        )

    query = query.order_by(
        Invoice.created_at.desc()
    )

    result = await db.execute(query)
    invoices = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="invoices/list.html",
        context={
            "invoices": invoices,
            "selected_environment": environment,
        },
    )

@router.get("/invoice_form")
async def invoice_form(request: Request):
    print("===== INVOICE FORM SESSION =====")
    print(dict(request.session))
    print("Province:", repr(request.session.get("tenant_province")))
    print("Address:", repr(request.session.get("tenant_address")))
    return templates.TemplateResponse(
        request=request,
        name="invoices/create.html",
        context={
            "today": date.today()
        }
    )

@router.post("/create")
async def create_invoice(request: Request):

    form = await request.form()

    parsed_data = parse_invoice_form(form)

    data = InvoiceCreate(**parsed_data)

    return templates.TemplateResponse(
        request=request,
        name="invoices/create.html",
        context={
            "today": date.today(),
            "success": True,
            "result": f"Invoice Created:\n{data}"
        }
    )
@router.get("/{invoice_id}/qr")
async def invoice_qr(
    invoice_id: uuid.UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    tenant_id = request.session.get("tenant_id")

    if not tenant_id:
        return JSONResponse(
            status_code=401,
            content={"message": "Tenant session not found."},
        )

    tenant_uuid = uuid.UUID(str(tenant_id))

    result = await db.execute(
        select(Invoice).where(
            Invoice.id == invoice_id,
            Invoice.tenant_id == tenant_uuid,
        )
    )

    invoice = result.scalar_one_or_none()

    if not invoice:
        return JSONResponse(
            status_code=404,
            content={"message": "Invoice not found."},
        )

    if invoice.status != "accepted" or not invoice.qr_data:
        return JSONResponse(
            status_code=404,
            content={
                "message": "QR code is not available for this invoice."
            },
        )

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(invoice.qr_data)
    qr.make(fit=False)

    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
    )

@router.get("/{invoice_id}")
async def invoice_detail(
    invoice_id: uuid.UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    tenant_id = request.session.get("tenant_id")

    if not tenant_id:
        return JSONResponse(
            status_code=401,
            content={"message": "Tenant session not found."},
        )

    tenant_uuid = uuid.UUID(str(tenant_id))

    result = await db.execute(
        select(Invoice)
        .options(selectinload(Invoice.items))
        .where(
            Invoice.id == invoice_id,
            Invoice.tenant_id == tenant_uuid,
        )
    )

    invoice = result.scalar_one_or_none()

    if not invoice:
        return JSONResponse(
            status_code=404,
            content={"message": "Invoice not found."},
        )

    return templates.TemplateResponse(
        request=request,
        name="invoices/detail.html",
        context={
            "invoice": invoice,
        },
    )





@router.get("/{invoice_id}/print")
async def invoice_print(
    invoice_id: uuid.UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    tenant_id = request.session.get("tenant_id")
    tenant_uuid = uuid.UUID(str(tenant_id))

    result = await db.execute(
        select(Invoice)
        .options(
            selectinload(Invoice.items)
        )
        .where(
            Invoice.id == invoice_id,
            Invoice.tenant_id == tenant_uuid,
        )
    )

    invoice = result.scalar_one_or_none()

    if not invoice:
        return JSONResponse(
            status_code=404,
            content={"message": "Invoice not found."},
        )

    return templates.TemplateResponse(
        request=request,
        name="invoices/print.html",
        context={
            "invoice": invoice,
        },
    )


