import uuid
from datetime import date
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from services.fbr_credentials import (
    FBREnvironment,
    get_fbr_token,
)


FBR_BASE_URL = "https://gw.fbr.gov.pk"


async def get_sale_type_rates(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    environment: FBREnvironment,
    transaction_type_id: int,
    province_code: int,
    invoice_date: date,
) -> list[dict[str, Any]]:

    token = await get_fbr_token(
        db=db,
        tenant_id=tenant_id,
        environment=environment,
    )

    url = f"{FBR_BASE_URL}/pdi/v2/SaleTypeToRate"

    params = {
        "date": invoice_date.strftime("%d-%b-%Y"),
        "transTypeId": transaction_type_id,
        "originationSupplier": province_code,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:

        response = await client.get(
            url,
            params=params,
            headers=headers,
        )

        response.raise_for_status()

        data = response.json()

    return [
        {
            "id": row.get("ratE_ID"),
            "description": row.get("ratE_DESC"),
            "value": row.get("ratE_VALUE"),
        }
        for row in data
    ]