import requests

url = "https://gw.fbr.gov.pk/pdi/v1/uom"

headers = {
    "Authorization": "Bearer c79f257e-a1d8-3c52-bc8b-61f3f826770a",
    "Accept": "application/json"
}

response = requests.get(
    url,
    headers=headers,
    timeout=30
)

response.raise_for_status()

uoms = response.json()

for uom in uoms:
    print(
        uom["uoM_ID"],
        uom["description"]
    )