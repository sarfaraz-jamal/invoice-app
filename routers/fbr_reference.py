import uuid
from datetime import date
from typing import Annotated, Literal

import httpx

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from models.tenant import Tenant

from services.fbr_reference import get_sale_type_rates
from services.fbr_credentials import FBRTokenNotConfiguredError, get_fbr_token
from services.fbr_hs_codes import FBRHSCodeError, search_hs_codes


router = APIRouter(
    prefix="/api/fbr/reference",
    tags=["FBR Reference"],
)


@router.get("/rates")
async def get_rates(
    request: Request,

    trans_type_id: Annotated[
        int,
        Query(gt=0),
    ],

    date_value: Annotated[
        date,
        Query(alias="date"),
    ],

    environment: Annotated[
        Literal["sandbox", "production"],
        Query(),
    ],

    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
):

    # =========================================================
    # GET ACTIVE TENANT FROM SESSION
    # =========================================================

    tenant_id_raw = request.session.get("tenant_id")

    if not tenant_id_raw:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )


    # Session stores UUID as a string
    try:
        tenant_id = uuid.UUID(tenant_id_raw)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid tenant ID in session",
        )


    # =========================================================
    # LOAD TENANT
    # =========================================================

    result = await db.execute(
        select(Tenant).where(
            Tenant.id == tenant_id,
            Tenant.is_active.is_(True),
        )
    )

    tenant = result.scalar_one_or_none()


    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found or inactive",
        )


    # =========================================================
    # SELLER PROVINCE
    # =========================================================

    if tenant.province_code is None:
        raise HTTPException(
            status_code=400,
            detail="Tenant province code is not configured",
        )


    # =========================================================
    # FBR RATE API
    # =========================================================

    try:

        rates = await get_sale_type_rates(
            db=db,
            tenant_id=tenant.id,
            environment=environment,
            transaction_type_id=trans_type_id,
            province_code=tenant.province_code,
            invoice_date=date_value,
        )

        return rates


    # =========================================================
    # TOKEN NOT CONFIGURED
    # =========================================================

    except FBRTokenNotConfiguredError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


    # =========================================================
    # FBR HTTP ERROR
    # =========================================================

    except httpx.HTTPStatusError as exc:

        print(
            "FBR RATE ERROR:",
            exc.response.status_code,
            exc.response.text,
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "FBR rate API failed "
                f"with status {exc.response.status_code}"
            ),
        )


    # =========================================================
    # NETWORK ERROR
    # =========================================================

    except httpx.RequestError as exc:

        print(
            "FBR CONNECTION ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=502,
            detail="Unable to connect to FBR",
        )

@router.get("/hs-codes")
async def get_hs_code_search(
    request: Request,
    q: str = Query(
        default="",
        max_length=100,
    ),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = request.session.get("tenant_id")

    if not tenant_id:
        raise HTTPException(
            status_code=401,
            detail="Tenant session not found.",
        )

    try:
        tenant_uuid = uuid.UUID(tenant_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid tenant ID in session.",
        ) from exc

    try:
        token = await get_fbr_token(
            db=db,
            tenant_id=tenant_uuid,
            environment="sandbox",
        )

    except FBRTokenNotConfiguredError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if not q.strip():
        return []

    try:
        results = await search_hs_codes(
            token=token,
            query=q,
            limit=30,
        )

    except FBRHSCodeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    return results