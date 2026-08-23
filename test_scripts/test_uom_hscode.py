import requests

TOKEN = "c79f257e-a1d8-3c52-bc8b-61f3f826770a"

hs_code = "7318.9000"
sale_type_id = 75  # example: Goods at standard rate (default)

url = "https://gw.fbr.gov.pk/pdi/v2/HS_UOM"

response = requests.get(
    url,
    params={
        "hs_code": hs_code,
        "annexure_id": sale_type_id,
    },
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json",
    },
    timeout=30,
)

print("Status:", response.status_code)
print("Response:", response.text)