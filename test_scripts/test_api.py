
import requests

url = "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata_sb"

token = "c79f257e-a1d8-3c52-bc8b-61f3f826770a"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

invoice = {
    "invoiceType": "Sale Invoice",
    "invoiceDate": "2026-08-18",
    "sellerNTNCNIC": "9568725",
    "sellerBusinessName": "A2TECH (PRIVATE) LIMITED",
    "sellerProvince": "Sindh",
    "sellerAddress": "House # 3/44, Big Plot, Shah Faisal Colony # 3, Pakistan",
    "buyerNTNCNIC": "4220155256289",
    "buyerBusinessName": "Sarfaraz Jamal",
    "buyerProvince": "Sindh",
    "buyerAddress": "3D 24/9 nazimabad",
    "buyerRegistrationType": "Unregistered",
    "invoiceRefNo": "a2tech_test_inv_002",
    "scenarioId": "SN002",
    "items": [
        {
            "hsCode": "6903.1000",
            "productDescription": "Inner Graphite Crucible Make: Alpha,USA",
            "rate": "18%",
            "uoM": "KG",
            "quantity": 5,
            "totalValues": 176256.60,
            "valueSalesExcludingST": 149370.00,
            "fixedNotifiedValueOrRetailPrice": 29874.00,
            "salesTaxApplicable": 26886.60,
            "salesTaxWithheldAtSource": 0.00,
            "extraTax": "",
            "furtherTax": 0,
            "sroScheduleNo": "",
            "fedPayable": 0,
            "discount": 0,
            "saleType": "Goods at standard rate (default)",
            "sroItemSerialNo": ""
        }
    ]
}

response = requests.post(
    url,
    headers=headers,
    json=invoice,
    timeout=30
)

print("Status Code:", response.status_code)
print("Response from API:")
print("-------------------------------")

try:
    print(response.json())
except ValueError:
    print(response.text)