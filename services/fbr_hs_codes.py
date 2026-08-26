import asyncio
import time
from typing import Any

import httpx


FBR_HS_CODES_URL = "https://gw.fbr.gov.pk/pdi/v1/itemdesccode"

# Cache HS codes for 6 hours
CACHE_TTL_SECONDS = 24 * 60 * 60


_hs_code_cache: list[dict[str, str]] | None = None
_hs_code_cache_expires_at: float = 0

# Prevent multiple users refreshing the cache simultaneously
_cache_lock = asyncio.Lock()


class FBRHSCodeError(Exception):
    pass


def _normalize_hs_codes(payload: Any) -> list[dict[str, str]]:
    """
    Convert the FBR response into our standard structure:

    [
        {
            "hs_code": "6903.1000",
            "description": "..."
        }
    ]
    """

    # FBR may return a list directly
    if isinstance(payload, list):
        items = payload

    # Or wrap the list inside an object
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

        # Handle possible FBR field-name variations
        hs_code = (
            item.get("hS_CODE")
            or item.get("hscode")
            or item.get("hsCode")
            or item.get("HSCode")
            or item.get("code")
        )

        description = (
            item.get("description")
            or item.get("itemDesc")
            or item.get("itemDescription")
            or item.get("desc")
        )

        if not hs_code:
            continue

        normalized.append(
            {
                "hs_code": str(hs_code).strip(),
                "description": str(description or "").strip(),
            }
        )

    return normalized


async def _fetch_hs_codes_from_fbr(
    token: str,
) -> list[dict[str, str]]:
    """
    Fetch the complete HS-code reference list from FBR.
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    try:

        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.get(
                FBR_HS_CODES_URL,
                headers=headers,
            )

            response.raise_for_status()

    except httpx.HTTPStatusError as exc:

        raise FBRHSCodeError(
            f"FBR HS Code API returned "
            f"{exc.response.status_code}: "
            f"{exc.response.text}"
        ) from exc

    except httpx.RequestError as exc:

        raise FBRHSCodeError(
            f"Could not connect to FBR HS Code API: {exc}"
        ) from exc

    try:
        payload = response.json()
        print("===== FBR HS CODE RAW RESPONSE =====")
        print(payload)
        print("====================================")

    except ValueError as exc:

        raise FBRHSCodeError(
            "FBR HS Code API returned invalid JSON."
        ) from exc

    hs_codes = _normalize_hs_codes(payload)

    if not hs_codes:
        raise FBRHSCodeError(
            "FBR HS Code API returned no usable HS codes."
        )

    return hs_codes


async def get_hs_codes(
    token: str,
) -> list[dict[str, str]]:
    """
    Return cached HS codes.

    Refresh from FBR when:
    - cache does not exist
    - cache has expired
    """

    global _hs_code_cache
    global _hs_code_cache_expires_at

    now = time.monotonic()

    # Fast cache hit
    if (
        _hs_code_cache is not None
        and now < _hs_code_cache_expires_at
    ):
        return _hs_code_cache

    # Only one request should refresh the cache
    async with _cache_lock:

        # Check again because another request may
        # have refreshed while we waited for the lock.
        now = time.monotonic()

        if (
            _hs_code_cache is not None
            and now < _hs_code_cache_expires_at
        ):
            return _hs_code_cache

        hs_codes = await _fetch_hs_codes_from_fbr(token)

        _hs_code_cache = hs_codes
        _hs_code_cache_expires_at = (
            time.monotonic() + CACHE_TTL_SECONDS
        )

        return _hs_code_cache


async def search_hs_codes(
    *,
    token: str,
    query: str,
    limit: int = 30,
) -> list[dict[str, str]]:
    """
    Search HS codes by either:

    - HS code
    - description

    Example:
        6903
        ceramic
        refractory
    """

    hs_codes = await get_hs_codes(token)

    query = query.strip().lower()

    if not query:
        return []

    matches: list[dict[str, str]] = []

    for item in hs_codes:

        hs_code = item["hs_code"].lower()
        description = item["description"].lower()

        if query in hs_code or query in description:

            matches.append(item)

            if len(matches) >= limit:
                break

    return matches