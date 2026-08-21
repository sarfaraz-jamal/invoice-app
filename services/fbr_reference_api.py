from datetime import date
from typing import Literal, Any

import httpx

from services.fbr_credentials import (
    get_fbr_token,
    FBREnvironment,
)


FBR_REFERENCE_BASE_URL = "https://gw.fbr.gov.pk/pdi"
FBR_DIST_BASE_URL = "https://gw.fbr.gov.pk/dist"
