import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    Boolean,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    currency: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True,
    )

    timezone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    ntn_cnic: Mapped[str | None] = mapped_column(
        String(20),
    )

    province: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
    )

    address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        
    )

    sandbox_environment_token: Mapped[str | None] = mapped_column(
        Text,
    )

    production_environment_token: Mapped[str | None] = mapped_column(
        Text,
    )