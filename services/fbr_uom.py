from typing import Any

import httpx


FBR_HS_UOM_URL = (
    "https://gw.fbr.gov.pk/pdi/v2/HS_UOM"
)


class FBRUOMError(Exception):
    pass


def _normalize_uoms(
    payload: Any,
) -> list[dict[str, str]]:

    if isinstance(payload, list):
        items = payload

    elif isinstance(payload, dict):
        items = (
            payload.get("data")
            or payload.get("result")
            or payload.get("items")
            or []
        )

    else:
        items = []


    normalized: list[dict[str, str]] = []


    for item in items:

        if not isinstance(item, dict):
            continue


        uom_id = (
            item.get("uoM_ID")
            or item.get("uom_id")
            or item.get("uomId")
            or item.get("id")
        )


        description = (
            item.get("description")
            or item.get("uoM_DESC")
            or item.get("uomDesc")
        )


        if uom_id is None:
            continue


        normalized.append(
            {
                "id": str(uom_id).strip(),
                "description": str(
                    description or ""
                ).strip(),
            }
        )


    return normalized


async def get_valid_uoms(
    *,
    token: str,
    hs_code: str,
    annexure_id: int,
) -> list[dict[str, str]]:

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


    params = {
        "hs_code": hs_code,
        "annexure_id": annexure_id,
    }


    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                FBR_HS_UOM_URL,
                headers=headers,
                params=params,
            )

            response.raise_for_status()


    except httpx.HTTPStatusError as exc:

        raise FBRUOMError(
            f"FBR HS/UOM API returned "
            f"{exc.response.status_code}: "
            f"{exc.response.text}"
        ) from exc


    except httpx.RequestError as exc:

        raise FBRUOMError(
            f"Could not connect to FBR "
            f"HS/UOM API: {exc}"
        ) from exc


    try:

        payload = response.json()

    except ValueError as exc:

        raise FBRUOMError(
            "FBR HS/UOM API returned invalid JSON."
        ) from exc


    return _normalize_uoms(payload)