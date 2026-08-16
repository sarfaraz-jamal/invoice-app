from typing import Annotated
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from schemas.invoice import InvoiceCreate
from datetime import date
from utils.form_parser import parse_invoice_form



router = APIRouter(
    tags=["Invoices"]
)

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def invoices_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="invoices/list.html"
    )

@router.get("/invoice_form")
async def invoice_form(request: Request):
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









