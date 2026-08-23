from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import httpx


FBR_SANDBOX_POST_URL = (
    "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata_sb"
)

FBR_PRODUCTION_POST_URL = (
    "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata"
)


# =========================================================
# RESULT
# =========================================================

@dataclass
class FBRSubmissionResult:
    success: bool
    invoice_number: str | None
    dated: str | None
    status_code: str | None
    status: str | None
    error_code: str | None
    error: str | None
    item_statuses: list[dict[str, Any]]
    raw_response: dict[str, Any]


# =========================================================
# EXCEPTION
# =========================================================

class FBRSubmissionError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: str | None = None,
        response: dict[str, Any] | None = None,
    ):
        super().__init__(message)

        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.response = response or {}


# =========================================================
# JSON HELPERS
# =========================================================

def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            key: _json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [
            _json_safe(item)
            for item in value
        ]

    return value


# =========================================================
# ENVIRONMENT
# =========================================================

def _normalize_environment(
    environment: str,
) -> str:

    environment = (
        environment or "sandbox"
    ).lower().strip()

    if environment not in {
        "sandbox",
        "production",
    }:
        raise FBRSubmissionError(
            f"Invalid FBR environment: {environment}"
        )

    return environment


# =========================================================
# TOKEN
# =========================================================

def _get_token(
    tenant,
    environment: str,
) -> str:

    if environment == "production":
        token = getattr(
            tenant,
            "production_environment_token",
            None,
        )

    else:
        token = getattr(
            tenant,
            "sandbox_environment_token",
            None,
        )

    if not token:
        raise FBRSubmissionError(
            f"FBR {environment} token is not configured for this tenant."
        )

    return token


# =========================================================
# ENDPOINT
# =========================================================

def _get_post_url(
    environment: str,
) -> str:

    if environment == "production":
        return FBR_PRODUCTION_POST_URL

    return FBR_SANDBOX_POST_URL


# =========================================================
# ERROR EXTRACTION
# =========================================================

def _extract_fbr_error(
    validation_response: dict[str, Any],
) -> str:

    main_error = validation_response.get(
        "error"
    )

    if main_error:
        return str(main_error)

    invoice_statuses = (
        validation_response.get(
            "invoiceStatuses"
        )
        or []
    )

    item_errors = []

    for item in invoice_statuses:

        error = item.get(
            "error"
        )

        if not error:
            continue

        item_no = item.get(
            "itemSNo"
        )

        if item_no:
            item_errors.append(
                f"Item {item_no}: {error}"
            )
        else:
            item_errors.append(
                str(error)
            )

    if item_errors:
        return "; ".join(
            item_errors
        )

    return "FBR rejected the invoice."


# =========================================================
# RESPONSE PARSER
# =========================================================

def _parse_response(
    data: dict[str, Any],
) -> FBRSubmissionResult:

    validation = (
        data.get(
            "validationResponse"
        )
        or {}
    )

    status = validation.get(
        "status"
    )

    status_code = validation.get(
        "statusCode"
    )

    error_code = validation.get(
        "errorCode"
    )

    error = validation.get(
        "error"
    )

    invoice_statuses = (
        validation.get(
            "invoiceStatuses"
        )
        or []
    )

    invoice_valid = (
        str(status).lower()
        == "valid"
    )

    items_valid = True

    for item in invoice_statuses:

        item_status = str(
            item.get(
                "status",
                "",
            )
        ).lower()

        item_status_code = str(
            item.get(
                "statusCode",
                "",
            )
        )

        if (
            item_status == "invalid"
            or item_status_code == "01"
        ):
            items_valid = False
            break

    success = (
        invoice_valid
        and items_valid
        and bool(
            data.get(
                "invoiceNumber"
            )
        )
    )

    return FBRSubmissionResult(
        success=success,

        invoice_number=data.get(
            "invoiceNumber"
        ),

        dated=data.get(
            "dated"
        ),

        status_code=status_code,

        status=status,

        error_code=error_code,

        error=error,

        item_statuses=invoice_statuses,

        raw_response=data,
    )


# =========================================================
# SUBMIT INVOICE
# =========================================================

async def submit_invoice(
    tenant,
    payload: dict[str, Any],
    environment: str,
) -> FBRSubmissionResult:

    # ---------------------------------------------
    # Normalize environment
    # ---------------------------------------------

    environment = (
        _normalize_environment(
            environment
        )
    )

    # ---------------------------------------------
    # Get tenant-specific token
    # ---------------------------------------------

    token = _get_token(
        tenant,
        environment,
    )

    # ---------------------------------------------
    # Select FBR endpoint
    # ---------------------------------------------

    url = _get_post_url(
        environment
    )

    # ---------------------------------------------
    # Convert payload to JSON-safe values
    # ---------------------------------------------

    payload = _json_safe(
        payload
    )

    headers = {
        "Authorization": (
            f"Bearer {token}"
        ),
        "Content-Type": (
            "application/json"
        ),
        "Accept": (
            "application/json"
        ),
    }

    # ---------------------------------------------
    # Submit request
    # ---------------------------------------------

    try:

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(
                30.0
            )
        ) as client:

            response = await client.post(
                url,
                json=payload,
                headers=headers,
            )

    except httpx.TimeoutException as exc:

        raise FBRSubmissionError(
            "FBR request timed out."
        ) from exc

    except httpx.RequestError as exc:

        raise FBRSubmissionError(
            f"Could not connect to FBR: {exc}"
        ) from exc

    # ---------------------------------------------
    # HTTP errors
    # ---------------------------------------------

    if response.status_code == 401:

        raise FBRSubmissionError(
            (
                "FBR authentication failed. "
                "Check the tenant token."
            ),
            status_code=401,
        )

    if response.status_code >= 500:

        raise FBRSubmissionError(
            (
                "FBR service returned "
                "a server error."
            ),
            status_code=(
                response.status_code
            ),
        )

    if response.status_code != 200:

        raise FBRSubmissionError(
            (
                "Unexpected response from FBR. "
                f"HTTP {response.status_code}"
            ),
            status_code=(
                response.status_code
            ),
        )

    # ---------------------------------------------
    # Parse JSON response
    # ---------------------------------------------

    try:

        data = response.json()

    except ValueError as exc:

        raise FBRSubmissionError(
            (
                "FBR returned an invalid "
                "JSON response."
            ),
            status_code=(
                response.status_code
            ),
        ) from exc

    # ---------------------------------------------
    # Parse FBR validation result
    # ---------------------------------------------

    result = _parse_response(
        data
    )

    # ---------------------------------------------
    # FBR rejected invoice
    # ---------------------------------------------

    if not result.success:

        validation = (
            data.get(
                "validationResponse"
            )
            or {}
        )

        error_message = (
            _extract_fbr_error(
                validation
            )
        )

        raise FBRSubmissionError(
            error_message,

            status_code=(
                response.status_code
            ),

            error_code=(
                result.error_code
            ),

            response=data,
        )

    return result