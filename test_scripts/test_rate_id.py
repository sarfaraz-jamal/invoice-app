import requests
import json

url = (
    "https://gw.fbr.gov.pk/pdi/v2/SaleTypeToRate"
    "?date=24-Aug-2026"
    "&transTypeId=18"
    "&originationSupplier=1"
)

token = "c79f257e-a1d8-3c52-bc8b-61f3f826770a"

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

response = requests.get(
    url,
    headers=headers,
    timeout=30
)

print("Status Code:", response.status_code)
print("Request URL:", response.url)
print("Response:")
print("-------------------------------")

response.raise_for_status()

data = response.json()

print(json.dumps(data, indent=4))

with open("sale_type_rates.json", "w", encoding="utf-8") as file:
    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=4
    )

print("\nSaved response to sale_type_rates.json")