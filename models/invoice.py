# models/invoice.py

import uuid
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy import (
    String,
    Text,
    Date,
    DateTime,
    Integer,
    Numeric,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

class Invoice(Base):
    __tablename__ = "invoices"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "invoice_number",
            name="uq_invoice_tenant_invoice_number",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # =========================
    # Application ownership
    # =========================

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )

    invoice_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # =========================
    # FBR invoice header
    # =========================

    invoice_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    invoice_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    invoice_ref_no: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    scenario_id: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # =========================
    # Seller snapshot
    # =========================

    seller_ntn_cnic: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    seller_business_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    seller_province: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    seller_address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # =========================
    # Buyer snapshot
    # =========================

    buyer_ntn_cnic: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    buyer_business_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    buyer_province: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    buyer_address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    buyer_registration_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # =========================
    # Invoice totals
    # =========================

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="PKR",
    )

    subtotal_excluding_st: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    total_sales_tax: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    total_further_tax: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    total_extra_tax: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    total_fed_payable: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    total_discount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    grand_total: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    # =========================
    # FBR sync status
    # =========================

    fbr_environment: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    fbr_request_payload: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    fbr_response_payload: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    qr_data: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
        index=True,
    )

    fbr_invoice_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    fbr_validation_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    fbr_submission_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    fbr_error_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    fbr_error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    last_validated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =========================
    # Audit
    # =========================

    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # =========================
    # Relationships
    # =========================

    items: Mapped[list["InvoiceItem"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="InvoiceItem.line_number",
    )

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    __table_args__ = (
        UniqueConstraint(
            "invoice_id",
            "line_number",
            name="uq_invoice_item_line_number",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_invoice_item_quantity_positive",
        ),
        CheckConstraint(
            "value_sales_excluding_st >= 0",
            name="ck_invoice_item_value_nonnegative",
        ),
        CheckConstraint(
            "sales_tax_applicable >= 0",
            name="ck_invoice_item_sales_tax_nonnegative",
        ),
        CheckConstraint(
            "sales_tax_withheld_at_source >= 0",
            name="ck_invoice_item_withheld_tax_nonnegative",
        ),
        CheckConstraint(
            "extra_tax >= 0",
            name="ck_invoice_item_extra_tax_nonnegative",
        ),
        CheckConstraint(
            "further_tax >= 0",
            name="ck_invoice_item_further_tax_nonnegative",
        ),
        CheckConstraint(
            "fed_payable >= 0",
            name="ck_invoice_item_fed_nonnegative",
        ),
        CheckConstraint(
            "discount >= 0",
            name="ck_invoice_item_discount_nonnegative",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "invoices.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    line_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # =========================
    # FBR item fields
    # =========================

    hs_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    product_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    rate: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    uom: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    total_values: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    value_sales_excluding_st: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    fixed_notified_value_or_retail_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    sales_tax_applicable: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    sales_tax_withheld_at_source: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    extra_tax: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    further_tax: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    sro_schedule_no: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    fed_payable: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    discount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    sale_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    sro_item_serial_no: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # =========================
    # Audit
    # =========================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # =========================
    # Relationship
    # =========================

    invoice: Mapped["Invoice"] = relationship(
        back_populates="items",
    )