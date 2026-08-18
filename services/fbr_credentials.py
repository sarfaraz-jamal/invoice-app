import uuid
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.tenant import Tenant


FBREnvironment = Literal[
    "sandbox",
    "production",
]


class FBRTokenNotConfiguredError(Exception):
    pass


async def get_fbr_token(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    environment: FBREnvironment,
) -> str:

    stmt = select(Tenant).where(
        Tenant.id == tenant_id,
        Tenant.is_active.is_(True),
    )

    result = await db.execute(stmt)

    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise FBRTokenNotConfiguredError(
            f"Tenant {tenant_id} not found or inactive"
        )

    if environment == "sandbox":
        token = tenant.sandbox_environment_token

    elif environment == "production":
        token = tenant.production_environment_token

    else:
        raise ValueError(
            "Environment must be 'sandbox' or 'production'"
        )

    if not token:
        raise FBRTokenNotConfiguredError(
            f"{environment.title()} FBR token "
            f"is not configured for tenant {tenant_id}"
        )

    return token