import requests
import json

url = (
    "https://gw.fbr.gov.pk/pdi/v2/SROItem"
    "?date=2026-08-24"
    "&sro_id=372"
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

try:
    data = response.json()
    print(data)

   

except Exception:
    print(response.text)