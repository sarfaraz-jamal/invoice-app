import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from models.invoice import Invoice, InvoiceItem


def decimal_value(value: Any) -> Decimal:
    if value in (None, ""):
        return Decimal("0.00")

    return Decimal(str(value))


async def create_invoice(
    *,
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID | None,
    payload: dict[str, Any],
    environment: str,
    invoice_number: str | None,
) -> Invoice:

    # ---------------------------------------------------------
    # VALIDATE INTERNAL / CLIENT INVOICE NUMBER
    # ---------------------------------------------------------

    invoice_number = (
        invoice_number or ""
    ).strip()

    if not invoice_number:
        raise ValueError(
            "Invoice number is required."
        )

    # ---------------------------------------------------------
    # CREATE INVOICE HEADER
    # ---------------------------------------------------------

    invoice = Invoice(
        tenant_id=tenant_id,

        invoice_number=invoice_number,

        invoice_type=payload["invoiceType"],

        invoice_date=datetime.strptime(
            payload["invoiceDate"],
            "%Y-%m-%d",
        ).date(),

        invoice_ref_no=payload.get(
            "invoiceRefNo"
        ),

        scenario_id=payload.get(
            "scenarioId"
        ),

        # Seller snapshot
        seller_ntn_cnic=payload[
            "sellerNTNCNIC"
        ],

        seller_business_name=payload[
            "sellerBusinessName"
        ],

        seller_province=payload[
            "sellerProvince"
        ],

        seller_address=payload[
            "sellerAddress"
        ],

        # Buyer snapshot
        buyer_ntn_cnic=payload.get(
            "buyerNTNCNIC"
        ),

        buyer_business_name=payload[
            "buyerBusinessName"
        ],

        buyer_province=payload[
            "buyerProvince"
        ],

        buyer_address=payload[
            "buyerAddress"
        ],

        buyer_registration_type=payload[
            "buyerRegistrationType"
        ],

        currency="PKR",

        fbr_environment=environment,

        fbr_request_payload=payload,

        status="submitting",

        created_by_user_id=user_id,
        updated_by_user_id=user_id,
    )

    db.add(invoice)

    # Flush so invoice.id becomes available
    await db.flush()

    # ---------------------------------------------------------
    # ITEMS
    # ---------------------------------------------------------

    items = payload.get(
        "items",
        []
    )

    if not items:
        raise ValueError(
            "Invoice must contain at least one item."
        )

    # ---------------------------------------------------------
    # TOTALS
    # ---------------------------------------------------------

    subtotal_excluding_st = Decimal(
        "0.00"
    )

    total_sales_tax = Decimal(
        "0.00"
    )

    total_further_tax = Decimal(
        "0.00"
    )

    total_extra_tax = Decimal(
        "0.00"
    )

    total_fed_payable = Decimal(
        "0.00"
    )

    total_discount = Decimal(
        "0.00"
    )

    grand_total = Decimal(
        "0.00"
    )

    # ---------------------------------------------------------
    # CREATE ITEMS
    # ---------------------------------------------------------

    for index, item_data in enumerate(
        items,
        start=1,
    ):

        item = InvoiceItem(
            invoice_id=invoice.id,

            line_number=index,

            hs_code=item_data[
                "hsCode"
            ],

            product_description=item_data[
                "productDescription"
            ],

            rate=item_data[
                "rate"
            ],

            uom=item_data[
                "uoM"
            ],

            quantity=decimal_value(
                item_data.get(
                    "quantity"
                )
            ),

            total_values=decimal_value(
                item_data.get(
                    "totalValues"
                )
            ),

            value_sales_excluding_st=(
                decimal_value(
                    item_data.get(
                        "valueSalesExcludingST"
                    )
                )
            ),

            fixed_notified_value_or_retail_price=(
                decimal_value(
                    item_data.get(
                        "fixedNotifiedValueOrRetailPrice"
                    )
                )
            ),

            sales_tax_applicable=(
                decimal_value(
                    item_data.get(
                        "salesTaxApplicable"
                    )
                )
            ),

            sales_tax_withheld_at_source=(
                decimal_value(
                    item_data.get(
                        "salesTaxWithheldAtSource"
                    )
                )
            ),

            extra_tax=decimal_value(
                item_data.get(
                    "extraTax"
                )
            ),

            further_tax=decimal_value(
                item_data.get(
                    "furtherTax"
                )
            ),

            sro_schedule_no=item_data.get(
                "sroScheduleNo"
            ),

            fed_payable=decimal_value(
                item_data.get(
                    "fedPayable"
                )
            ),

            discount=decimal_value(
                item_data.get(
                    "discount"
                )
            ),

            sale_type=item_data[
                "saleType"
            ],

            sro_item_serial_no=item_data.get(
                "sroItemSerialNo"
            ),
        )

        db.add(item)

        # -----------------------------------------------------
        # ACCUMULATE TOTALS
        # -----------------------------------------------------

        subtotal_excluding_st += (
            item.value_sales_excluding_st
        )

        total_sales_tax += (
            item.sales_tax_applicable
        )

        total_further_tax += (
            item.further_tax
        )

        total_extra_tax += (
            item.extra_tax
        )

        total_fed_payable += (
            item.fed_payable
        )

        total_discount += (
            item.discount
        )

        grand_total += (
            item.total_values
        )

    # ---------------------------------------------------------
    # ASSIGN TOTALS
    # ---------------------------------------------------------

    invoice.subtotal_excluding_st = (
        subtotal_excluding_st
    )

    invoice.total_sales_tax = (
        total_sales_tax
    )

    invoice.total_further_tax = (
        total_further_tax
    )

    invoice.total_extra_tax = (
        total_extra_tax
    )

    invoice.total_fed_payable = (
        total_fed_payable
    )

    invoice.total_discount = (
        total_discount
    )

    invoice.grand_total = (
        grand_total
    )

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    await db.commit()

    await db.refresh(
        invoice
    )

    return invoice


async def mark_invoice_accepted(
    *,
    db: AsyncSession,
    invoice: Invoice,
    fbr_result,
) -> None:

    invoice.status = "accepted"

    invoice.fbr_invoice_number = (
        fbr_result.invoice_number
    )

    # QR currently contains FBR invoice number
    invoice.qr_data = (
        fbr_result.invoice_number
    )

    invoice.fbr_validation_status = (
        fbr_result.status
    )

    invoice.fbr_submission_status = (
        fbr_result.status
    )

    invoice.fbr_response_payload = (
        fbr_result.raw_response
    )

    invoice.fbr_error_code = None
    invoice.fbr_error_message = None

    invoice.submitted_at = (
        datetime.now(
            timezone.utc
        )
    )

    await db.commit()


async def mark_invoice_failed(
    *,
    db: AsyncSession,
    invoice: Invoice,
    error,
) -> None:

    # ---------------------------------------------------------
    # FBR RESPONDED -> REJECTED
    # ---------------------------------------------------------

    if error.response:

        invoice.status = "rejected"

        invoice.fbr_response_payload = (
            error.response
        )

        validation_response = (
            error.response.get(
                "validationResponse",
                {},
            )
        )

        fbr_status = (
            validation_response.get(
                "status"
            )
        )

        invoice.fbr_validation_status = (
            fbr_status
        )

        invoice.fbr_submission_status = (
            fbr_status
        )

    # ---------------------------------------------------------
    # NO FBR RESPONSE -> TECHNICAL FAILURE
    # ---------------------------------------------------------

    else:

        invoice.status = "failed"

    invoice.fbr_error_code = (
        error.error_code
    )

    invoice.fbr_error_message = (
        error.message
    )

    await db.commit()