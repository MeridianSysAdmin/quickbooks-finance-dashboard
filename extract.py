import os
import sys
import json
import requests

entity = sys.argv[1]   # Customer, Invoice or Account

token = os.environ["QBO_ACCESS_TOKEN"]
realm_id = os.environ["QBO_REALM_ID"]

url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/query"
params = {"query": f"select * from {entity} STARTPOSITION 1 MAXRESULTS 1000"}
headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

response = requests.get(url, params=params, headers=headers)
print("Status:", response.status_code)
response.raise_for_status()

data = response.json()
rows = data.get("QueryResponse", {}).get(entity, [])
print(f"{entity} records found:", len(rows))

with open(f"data/{entity}.json", "w") as f:
    json.dump(data, f, indent=2)
print(f"Saved to data/{entity}.json")