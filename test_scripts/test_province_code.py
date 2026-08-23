import requests

url = "https://gw.fbr.gov.pk/pdi/v1/provinces"
token = "c79f257e-a1d8-3c52-bc8b-61f3f826770a"

response = requests.get(
    url,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    timeout=30
)

print(response.json())

"""
[{'stateProvinceCode': 2, 'stateProvinceDesc': 'BALOCHISTAN'}, 
 {'stateProvinceCode': 4, 'stateProvinceDesc': 'AZAD JAMMU AND KASHMIR'}, 
 {'stateProvinceCode': 5, 'stateProvinceDesc': 'CAPITAL TERRITORY'}, 
 {'stateProvinceCode': 6, 'stateProvinceDesc': 'KHYBER PAKHTUNKHWA'}, 
 {'stateProvinceCode': 7, 'stateProvinceDesc': 'PUNJAB'}, 
 {'stateProvinceCode': 8, 'stateProvinceDesc': 'SINDH'}, 
 {'stateProvinceCode': 9, 'stateProvinceDesc': 'GILGIT BALTISTAN'}]
 """