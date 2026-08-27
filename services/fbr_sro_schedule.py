from typing import Any

import httpx

from datetime import datetime


FBR_SRO_SCHEDULE_URL = (
    "https://gw.fbr.gov.pk/pdi/v1/SroSchedule"
)


class FBRSROScheduleError(Exception):
    pass


def _normalize_sro_schedules(
    payload: Any,
) -> list[dict[str, str]]:
    """
    Normalize the FBR response into:

    [
        {
            "id": "7",
            "description": "Zero Rated Gas"
        },
        {
            "id": "8",
            "description": "5th Schedule"
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


        sro_id = (
            item.get("srO_ID")
            or item.get("sro_id")
            or item.get("sroId")
            or item.get("id")
        )


        description = (
            item.get("srO_DESC")
            or item.get("sro_desc")
            or item.get("sroDesc")
            or item.get("description")
        )


        if sro_id is None:
            continue


        normalized.append(
            {
                "id": str(sro_id).strip(),
                "description": str(
                    description or ""
                ).strip(),
            }
        )


    return normalized


async def get_sro_schedules(
    *,
    token: str,
    rate_id: int,
    date: str,
) -> list[dict[str, str]]:
    """
    Fetch valid SRO schedules from FBR.

    Required by FBR:
    - rate_id
    - date
    - origination_supplier_csv
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    try:

        parsed_date = datetime.strptime(
            date,
            "%Y-%m-%d",
        )

        fbr_date = parsed_date.strftime(
            "%d-%b-%Y"
        )

    except ValueError as exc:
        raise FBRSROScheduleError(
            f"Invalid date format: {date}. "
            "Expected YYYY-MM-DD."
        ) from exc


    params = {
        "rate_id": rate_id,
        "date": fbr_date,
        "origination_supplier_csv": 1,
    }


    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                FBR_SRO_SCHEDULE_URL,
                headers=headers,
                params=params,
            )

            response.raise_for_status()


    except httpx.HTTPStatusError as exc:

        raise FBRSROScheduleError(
            f"FBR SRO Schedule API returned "
            f"{exc.response.status_code}: "
            f"{exc.response.text}"
        ) from exc


    except httpx.RequestError as exc:

        raise FBRSROScheduleError(
            f"Could not connect to FBR "
            f"SRO Schedule API: {exc}"
        ) from exc


    try:

        payload = response.json()

    except ValueError as exc:

        raise FBRSROScheduleError(
            "FBR SRO Schedule API returned "
            "invalid JSON."
        ) from exc


    return _normalize_sro_schedules(
        payload
    )