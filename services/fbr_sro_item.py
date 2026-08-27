from typing import Any

import httpx


FBR_SRO_ITEM_URL = (
    "https://gw.fbr.gov.pk/pdi/v2/SROItem"
)


class FBRSROItemError(Exception):
    pass


def _normalize_sro_items(
    payload: Any,
) -> list[dict[str, str]]:
    """
    Normalize FBR response into:

    [
        {
            "id": "17853",
            "description": "50"
        }
    ]
    """

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


        item_id = (
            item.get("srO_ITEM_ID")
            or item.get("sro_item_id")
            or item.get("sroItemId")
            or item.get("id")
        )


        description = (
            item.get("srO_ITEM_DESC")
            or item.get("sro_item_desc")
            or item.get("sroItemDesc")
            or item.get("description")
        )


        if item_id is None:
            continue


        normalized.append(
            {
                "id": str(item_id).strip(),
                "description": str(
                    description or ""
                ).strip(),
            }
        )


    return normalized


async def get_sro_items(
    *,
    token: str,
    sro_id: int,
    date: str,
) -> list[dict[str, str]]:
    """
    Fetch valid SRO item serials from FBR.

    FBR requires:
    - date
    - sro_id
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


    params = {
        "date": date,
        "sro_id": sro_id,
    }


    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                FBR_SRO_ITEM_URL,
                headers=headers,
                params=params,
            )

            response.raise_for_status()


    except httpx.HTTPStatusError as exc:

        raise FBRSROItemError(
            f"FBR SRO Item API returned "
            f"{exc.response.status_code}: "
            f"{exc.response.text}"
        ) from exc


    except httpx.RequestError as exc:

        raise FBRSROItemError(
            f"Could not connect to FBR "
            f"SRO Item API: {exc}"
        ) from exc


    try:

        payload = response.json()

    except ValueError as exc:

        raise FBRSROItemError(
            "FBR SRO Item API returned "
            "invalid JSON."
        ) from exc


    return _normalize_sro_items(
        payload
    )