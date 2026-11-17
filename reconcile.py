import json
import os
from decimal import Decimal

import pyodbc

server = os.environ.get("SQL_SERVER", r"localhost\MSSQLSERVER01")
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={server};DATABASE=FinanceDemo;"
    "Trusted_Connection=yes;TrustServerCertificate=yes;"
)
cur = conn.cursor()


def source(entity):
    """Records from the QuickBooks JSON file (the source)."""
    with open(f"data/{entity}.json", encoding="utf-8") as f:
        return json.load(f).get("QueryResponse", {}).get(entity, [])


def money(value):
    """Round to cents so 10.1 and 10.10 compare as equal."""
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def scalar(sql):
    """Run a query that returns one value."""
    return cur.execute(sql).fetchone()[0]


results = []


def check(name, src, tgt):
    diff = src - tgt
    results.append((name, str(src), str(tgt), str(diff), "PASS" if diff == 0 else "EXCEPTION"))


# 1. Row counts: nothing was dropped
for entity in ("Customer", "Invoice", "Account"):
    check(f"{entity} row count", len(source(entity)), scalar(f"SELECT COUNT(*) FROM dbo.{entity}"))

# 2-3. Invoice money: nothing changed in transit
invoices = source("Invoice")
check("Invoice total amount",
      sum(money(i.get("TotalAmt")) for i in invoices),
      money(scalar("SELECT SUM(TotalAmt) FROM dbo.Invoice")))
check("Invoice open balance",
      sum(money(i.get("Balance")) for i in invoices),
      money(scalar("SELECT SUM(Balance) FROM dbo.Invoice")))

# 4. Orphans: every invoice belongs to a customer
check("Invoices with no matching customer", 0, scalar(
    "SELECT COUNT(*) FROM dbo.Invoice i LEFT JOIN dbo.Customer c ON c.Id = i.CustomerId "
    "WHERE c.Id IS NULL"))

# 5. Tie-outs inside SQL: customer list, invoices and ledger agree
customer_total = money(scalar("SELECT SUM(Balance) FROM dbo.Customer"))
check("Customer balances vs open invoices", customer_total,
      money(scalar("SELECT SUM(Balance) FROM dbo.Invoice")))
check("A/R account vs customer balances",
      money(scalar("SELECT SUM(CurrentBalance) FROM dbo.Account "
                   "WHERE AccountType = 'Accounts Receivable'")),
      customer_total)

# Save results so Power BI can show them later
cur.execute("""
IF OBJECT_ID('dbo.ReconResults') IS NULL
CREATE TABLE dbo.ReconResults (
    RunAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    CheckName   NVARCHAR(100) NOT NULL,
    SourceValue NVARCHAR(50)  NULL,
    TargetValue NVARCHAR(50)  NULL,
    Difference  NVARCHAR(50)  NULL,
    Status      NVARCHAR(20)  NOT NULL
)""")
cur.executemany(
    "INSERT INTO dbo.ReconResults (CheckName, SourceValue, TargetValue, Difference, Status) "
    "VALUES (?, ?, ?, ?, ?)", results)
conn.commit()

print(f"{'Check':40} {'Source':>12} {'Target':>12} {'Diff':>10}  Status")
for name, src, tgt, diff, status in results:
    print(f"{name:40} {src:>12} {tgt:>12} {diff:>10}  {status}")

# Customers whose balance doesn't match their open invoices
print("\nCustomer exceptions:")
rows = cur.execute("""
SELECT c.DisplayName, COALESCE(c.Balance, 0), COALESCE(SUM(i.Balance), 0)
FROM dbo.Customer c LEFT JOIN dbo.Invoice i ON i.CustomerId = c.Id
GROUP BY c.Id, c.DisplayName, c.Balance
HAVING COALESCE(c.Balance, 0) <> COALESCE(SUM(i.Balance), 0)""").fetchall()
for name, balance, open_invoices in rows:
    print(f"  {name}: customer balance {balance}, open invoices {open_invoices}")
print(f"  {len(rows)} customer(s) with a difference")
conn.close()