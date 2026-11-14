import os
import json
import requests

# Read secrets from environment variables, never from the code
token = os.environ["QBO_ACCESS_TOKEN"]
realm_id = os.environ["QBO_REALM_ID"]

url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/query"
params = {"query": "select * from Customer"}
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

response = requests.get(url, params=params, headers=headers)
print("Status:", response.status_code)
response.raise_for_status()

data = response.json()
customers = data.get("QueryResponse", {}).get("Customer", [])
print("Customers found:", len(customers))

with open("data/customers.json", "w") as f:
    json.dump(data, f, indent=2)
print("Saved to data/customers.json")