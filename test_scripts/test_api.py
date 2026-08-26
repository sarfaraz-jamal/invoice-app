
import requests

url = "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata_sb"

token = "c79f257e-a1d8-3c52-bc8b-61f3f826770a"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

invoice = {
    "invoiceType": "Sale Invoice",
    "invoiceDate": "2026-08-24",

    "sellerNTNCNIC": "9568725",
    "sellerBusinessName": "A2TECH (PRIVATE) LIMITED",
    "sellerProvince": "Sindh",
    "sellerAddress": "House # 3/44, Big Plot, Shah Faisal Colony # 3, Pakistan",

    "buyerNTNCNIC": "1435809",
    "buyerBusinessName": "Fauji Fertlizer Company Ltd",
    "buyerProvince": "Sindh",
    "buyerAddress": "EZ/I/P-1 Eastern Zone, Bin Qasim, Karachi-75020, Pakistan",
    "buyerRegistrationType": "Registered",

    "invoiceRefNo": "",
    "scenarioId": "SN005",

    "items": [
        {
            "hsCode": "0102.2930",
            "productDescription": "Inner Graphite Crucible",
            "rate": "10%",
            "uoM": "KG",
            "quantity": 1,

            "totalValues": 572241.98,
            "valueSalesExcludingST": 544992.86,
            "fixedNotifiedValueOrRetailPrice": 0,
            "salesTaxApplicable": 27249.62,
            "salesTaxWithheldAtSource": 0,

            "extraTax": 0,
            "furtherTax": 0,
            "sroScheduleNo": "SRO364",
            "fedPayable": 0,
            "discount": 0,

            "saleType": "Goods at Reduced Rate",
            "sroItemSerialNo": "84(i)",
        }
    ],
}

# invoice2 = {
#     "invoiceType": "Sale Invoice",
#     "invoiceDate": "2026-08-24",
#     "sellerNTNCNIC": "9568725",
#     "sellerBusinessName": "A2TECH (PRIVATE) LIMITED",
#     "sellerProvince": "Sindh",
#     "sellerAddress": "House # 3/44, Big Plot, Shah Faisal Colony # 3, Pakistan",
#     "buyerNTNCNIC": "4220155256289",
#     "buyerBusinessName": "FFC",
#     "buyerProvince": "Sindh",
#     "buyerAddress": "EZ/I/P-1 Eastern Zone, Bin Qasim, Karachi-75020, Pakistan	",
#     "buyerRegistrationType": "Unregistered",
#     "invoiceRefNo": "a2tech_test_inv_001",
#     "scenarioId": "SN002",
#     "items": [
#         {
#             "hsCode": "6903.1000",
#             "productDescription": "Inner Graphite Crucible (Dimensions: H=0.623"""" x OD=0.50"""") (100 / Pack) Make: Alpha, USA",
#             "rate": "18%",
#             "uoM": "KG",
#             "quantity": 1,
#             "totalValues":   573675.88 ,
#             "valueSalesExcludingST":   486166.00 ,
#             "fixedNotifiedValueOrRetailPrice":   486166.00 ,
#             "salesTaxApplicable":   87509.88 ,
#             "salesTaxWithheldAtSource": 0.00,
#             "extraTax": "",
#             "furtherTax": 0,
#             "sroScheduleNo": "",
#             "fedPayable": 0,
#             "discount": 0,
#             "saleType": "Goods at standard rate (default)",
#             "sroItemSerialNo": ""
#         }
#     ]
# }

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
except Exception:
    print(response.text)