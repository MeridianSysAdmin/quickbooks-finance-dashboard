import os
import json
import pyodbc

server = os.environ.get("SQL_SERVER", "localhost")
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={server};DATABASE=FinanceDemo;"
    "Trusted_Connection=yes;TrustServerCertificate=yes;"
)
cur = conn.cursor()

def read(entity):
    with open(f"data/{entity}.json") as f:
        return json.load(f).get("QueryResponse", {}).get(entity, [])

# Customers
cur.execute("DELETE FROM dbo.Customer")
for c in read("Customer"):
    cur.execute(
        "INSERT INTO dbo.Customer (Id, DisplayName, Balance, Active) VALUES (?, ?, ?, ?)",
        c["Id"], c.get("DisplayName"), c.get("Balance"), c.get("Active"),
    )

# Invoices
cur.execute("DELETE FROM dbo.Invoice")
for i in read("Invoice"):
    cur.execute(
        "INSERT INTO dbo.Invoice (Id, DocNumber, CustomerId, TxnDate, DueDate, TotalAmt, Balance) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        i["Id"], i.get("DocNumber"), i.get("CustomerRef", {}).get("value"),
        i.get("TxnDate"), i.get("DueDate"), i.get("TotalAmt"), i.get("Balance"),
    )

# Accounts
cur.execute("DELETE FROM dbo.Account")
for a in read("Account"):
    cur.execute(
        "INSERT INTO dbo.Account (Id, Name, AccountType, Classification, CurrentBalance, Active) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        a["Id"], a.get("Name"), a.get("AccountType"), a.get("Classification"),
        a.get("CurrentBalance"), a.get("Active"),
    )

conn.commit()
for table in ("Customer", "Invoice", "Account"):
    count = cur.execute(f"SELECT COUNT(*) FROM dbo.{table}").fetchone()[0]
    print(f"{table}: {count} rows in SQL")
conn.close()