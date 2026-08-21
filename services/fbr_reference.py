from datetime import date
from typing import Literal, Any

import httpx

from services.fbr_credentials import (
    get_fbr_token,
    FBREnvironment,
)


FBR_REFERENCE_BASE_URL = "https://gw.fbr.gov.pk/pdi"
FBR_DIST_BASE_URL = "https://gw.fbr.gov.pk/dist"


class FBRReferenceAPIError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: Any = None,
    ):
        self.status_code = status_code
        self.response_body = response_body

        super().__init__(message)


class FBRReferenceService:
    """
    FBR Digital Invoicing Reference API service.

    Environment determines which tenant token is used.
    Reference API URLs themselves remain FBR endpoints.
    """

    def __init__(
        self,
        db,
        tenant_id: int,
        environment: FBREnvironment,
        timeout: float = 30.0,
    ):
        self.db = db
        self.tenant_id = tenant_id
        self.environment = environment
        self.timeout = timeout

    async def _headers(self) -> dict[str, str]:
        token = await get_fbr_token(
            db=self.db,
            tenant_id=self.tenant_id,
            environment=self.environment,
        )

        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    async def _get(
        self,
        url: str,
        *,
        params: dict | None = None,
        json_body: dict | None = None,
    ) -> Any:

        headers = await self._headers()

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:

                response = await client.request(
                    method="GET",
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_body,
                )

        except httpx.RequestError as exc:
            raise FBRReferenceAPIError(
                f"Unable to connect to FBR: {exc}"
            ) from exc

        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text

        if not response.is_success:
            raise FBRReferenceAPIError(
                message="FBR reference API request failed",
                status_code=response.status_code,
                response_body=response_data,
            )

        return response_data

    # ---------------------------------------------------------
    # 5.1 Province Code
    # ---------------------------------------------------------

    async def get_provinces(self):
        """
        GET /pdi/v1/provinces
        """

        return await self._get(
            f"{FBR_REFERENCE_BASE_URL}/v1/provinces"
        )

    # ---------------------------------------------------------
    # 5.2 Document Type
    # ---------------------------------------------------------

    async def get_document_types(self):
        """
        GET /pdi/v1/doctypecode
        """

        return await self._get(
            f"{FBR_REFERENCE_BASE_URL}/v1/doctypecode"
        )

    # ---------------------------------------------------------
    # 5.3 Item / HS Codes
    # ---------------------------------------------------------

    async def get_hs_codes(self):
        """
        GET /pdi/v1/itemdesccode

        Returns HS codes and their descriptions.
        """

        return await self._get(
            f"{FBR_REFERENCE_BASE_URL}/v1/itemdesccode"
        )

    # ---------------------------------------------------------
    # 5.4 SRO Item Code
    # ---------------------------------------------------------

    async def get_sro_item_codes(self):
        """
        GET /pdi/v1/sroitemcode
        """

        return await self._get(
            f"{FBR_REFERENCE_BASE_URL}/v1/sroitemcode"
        )

    # ---------------------------------------------------------
    # 5.5 Transaction Types / Sale Types
    # ---------------------------------------------------------

    async def get_transaction_types(self):
        """
        GET /pdi/v1/transtypecode
        """

        return await self._get(
            f"{FBR_REFERENCE_BASE_URL}/v1/transtypecode"
        )

    # ---------------------------------------------------------
    # 5.6 Units of Measurement
    # ---------------------------------------------------------

    async def get_uoms(self):
        """
        GET /pdi/v1/uom
        """

        return await self._get(
            f"{FBR_REFERENCE_BASE_URL}/v1/uom"
        )

    # ---------------------------------------------------------
    # 5.7 SRO Schedule
    # ---------------------------------------------------------

    async def get_sro_schedule(
        self,
        rate_id: int,
        invoice_date: str | date,
        origination_supplier: int,
    ):
        """
        GET /pdi/v1/SroSchedule

        FBR parameters:
            rate_id
            date
            origination_supplier_csv
        """

        invoice_date = self._format_fbr_date(
            invoice_date
        )

        params = {
            "rate_id": rate_id,
            "date": invoice_date,
            "origination_supplier_csv": (
                origination_supplier
            ),
        }

        return await self._get(
            f"{FBR_REFERENCE_BASE_URL}/v1/SroSchedule",
            params=params,
        )

    # ---------------------------------------------------------
    # 5.8 Sale Type -> Rate
    # ---------------------------------------------------------

    async def get_rates(
        self,
        transaction_type_id: int,
        invoice_date: str | date,
        origination_supplier: int,
    ):
        """
        GET /pdi/v2/SaleTypeToRate

        Returns valid rates for a transaction/sale type.
        """

        invoice_date = self._format_fbr_date(
            invoice_date
        )

        params = {
            "date": invoice_date,
            "transTypeId": transaction_type_id,
            "originationSupplier": (
                origination_supplier
            ),
        }

        return await self._get(
            f"{FBR_REFERENCE_BASE_URL}/v2/SaleTypeToRate",
            params=params,
        )

    # ---------------------------------------------------------
    # 5.9 HS Code -> UOM
    # ---------------------------------------------------------

    async def get_uoms_for_hs_code(
        self,
        hs_code: str,
        annexure_id: int,
    ):
        """
        GET /pdi/v2/HS_UOM

        Example:

            hs_code = "6903.1000"
            annexure_id = 3

        Returns valid UOM(s) for that HS code.
        """

        params = {
            "hs_code": hs_code,
            "annexure_id": annexure_id,
        }

        return await self._get(
            f"{FBR_REFERENCE_BASE_URL}/v2/HS_UOM",
            params=params,
        )

    # ---------------------------------------------------------
    # 5.10 SRO Items
    # ---------------------------------------------------------

    async def get_sro_items(
        self,
        sro_id: int,
        invoice_date: str | date,
    ):
        """
        GET /pdi/v2/SROItem
        """

        invoice_date = self._format_iso_date(
            invoice_date
        )

        params = {
            "date": invoice_date,
            "sro_id": sro_id,
        }

        return await self._get(
            f"{FBR_REFERENCE_BASE_URL}/v2/SROItem",
            params=params,
        )

    # ---------------------------------------------------------
    # 5.11 Sales Tax ATL Status
    # ---------------------------------------------------------

    async def get_statl_status(
        self,
        registration_number: str,
        check_date: str | date,
    ):
        """
        GET /dist/v1/statl

        FBR documentation shows a JSON body with the GET request.
        """

        check_date = self._format_iso_date(
            check_date
        )

        body = {
            "regno": registration_number,
            "date": check_date,
        }

        return await self._get(
            f"{FBR_DIST_BASE_URL}/v1/statl",
            json_body=body,
        )

    # ---------------------------------------------------------
    # 5.12 Registration Type
    # ---------------------------------------------------------

    async def get_registration_type(
        self,
        registration_number: str,
    ):
        """
        GET /dist/v1/Get_Reg_Type

        Returns:
            Registered
            or
            unregistered
        """

        body = {
            "Registration_No": registration_number
        }

        return await self._get(
            f"{FBR_DIST_BASE_URL}/v1/Get_Reg_Type",
            json_body=body,
        )

    # ---------------------------------------------------------
    # Internal utilities
    # ---------------------------------------------------------

    @staticmethod
    def _format_iso_date(
        value: str | date,
    ) -> str:
        """
        FBR invoice-style date:
        YYYY-MM-DD
        """

        if isinstance(value, date):
            return value.strftime("%Y-%m-%d")

        return value

    @staticmethod
    def _format_fbr_date(
        value: str | date,
    ) -> str:
        """
        Certain FBR reference APIs show dates such as:

            24-Feb-2024

        If a Python date object is supplied, convert to this
        format.

        Strings are passed through unchanged.
        """

        if isinstance(value, date):
            return value.strftime("%d-%b-%Y")

        return value