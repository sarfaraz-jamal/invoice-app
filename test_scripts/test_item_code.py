import requests
import json

url = "https://gw.fbr.gov.pk/pdi/v1/itemdesccode"

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

response.raise_for_status()

data = response.json()

with open("hs_codes.json", "w", encoding="utf-8") as file:
    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=4
    )

print(f"Saved {len(data)} HS codes to hs_codes.json")