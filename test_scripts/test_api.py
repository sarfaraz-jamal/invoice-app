
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

invoice2 = {
 
  "invoiceType": "Sale Invoice",
  "invoiceDate": "2026-08-26",
  "sellerNTNCNIC": "9568725",
  "sellerBusinessName": "A2 TECH (PRIVATE) LIMITED",
  "sellerProvince": "SINDH",
  "sellerAddress": "House # 3/44, Big Plot, Shah Faisal Colony # 3, Pakistan",
  "buyerNTNCNIC": "1435809",
  "buyerBusinessName": "sss enterprises",
  "buyerProvince": "SINDH",
  "buyerAddress": "8B, 8th floor, Mughlia Arcade, 1/19, 3A, Nazimabad no. 3",
  "buyerRegistrationType": "Registered",
  "items": [
    {
    "hsCode": "8472.3000",
    "productDescription": "PENCIL SHARPENER",
    "rate": "10%",
    "uoM": "Numbers, pieces, units",
    "quantity": 1.0,
    "totalValues": 1320.0,
    "valueSalesExcludingST": 1200.0,
    "fixedNotifiedValueOrRetailPrice": 1200.0,
    "salesTaxApplicable": 120.0,
    "salesTaxWithheldAtSource": 0.0,
    "extraTax": "",
    "furtherTax": 0.0,
    "fedPayable": 0.0,
    "discount": 0.0,
    "sroScheduleNo": "EIGHTH SCHEDULE Table 1",
    "saleType": "Goods at Reduced Rate",
    "sroItemSerialNo": "84(i)"
}
  ],
  "scenarioId": "SN005"
}

# invoice3 = {
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
    json=invoice2,
    timeout=30
)

print("Status Code:", response.status_code)
print("Response from API:")
print("-------------------------------")

try:
    print(response.json())
except Exception:
    print(response.text)