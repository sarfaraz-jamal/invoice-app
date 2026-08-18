from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TenantFBRCredentials(Base):
    __tablename__ = "tenant_fbr_credentials"

    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id"),
        primary_key=True,
    )

    sandbox_token: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    production_token: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )