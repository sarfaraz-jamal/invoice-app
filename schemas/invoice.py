from datetime import date
from pydantic import BaseModel, model_validator


class InvoiceItem(BaseModel):
    hsCode: str
    productDescription: str
    rate: str
    uoM: str
    quantity: int

    totalValues: float
    valueSalesExcludingST: float
    fixedNotifiedValueOrRetailPrice: float

    salesTaxApplicable: int
    salesTaxWithheldAtSource: float

    # Optional fields
    extraTax: float | None = None
    furtherTax: float | None = None
    sroScheduleNo: str | None = None
    fedPayable: float | None = None
    discount: float | None = None

    saleType: str

    sroItemSerialNo: str | None = None


class InvoiceCreate(BaseModel):
    invoiceType: str
    invoiceDate: date

    sellerNTNCNIC: str
    sellerBusinessName: str
    sellerProvince: str
    sellerAddress: str

    # Optional when buyer is Unregistered
    buyerNTNCNIC: str | None = None

    buyerBusinessName: str
    buyerProvince: str
    buyerAddress: str
    buyerRegistrationType: str

    # Required only for Debit Note
    invoiceRefNo: str | None = None

    # Required only in Sandbox
    scenarioId: str | None = None

    items: list[InvoiceItem]

    @model_validator(mode="after")
    def validate_invoice(self):

        # buyer NTN/CNIC required unless unregistered
        if (
            self.buyerRegistrationType.lower() != "unregistered"
            and not self.buyerNTNCNIC
        ):
            raise ValueError(
                "buyerNTNCNIC is required for registered buyers"
            )

        # invoiceRefNo required for Debit Note
        if (
            self.invoiceType.lower() == "debit note"
            and not self.invoiceRefNo
        ):
            raise ValueError(
                "invoiceRefNo is required for Debit Note"
            )

        return self