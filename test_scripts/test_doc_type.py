import requests

url = "https://gw.fbr.gov.pk/pdi/v1/doctypecode"

token = "c79f257e-a1d8-3c52-bc8b-61f3f826770a"

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

response = requests.get(
    url,
    headers=headers,
    timeout=30
)

print("Status:", response.status_code)

response.raise_for_status()

data = response.json()

print(data)