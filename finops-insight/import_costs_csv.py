import pandas as pd
from sqlalchemy import text
from app.database import SessionLocal

CSV_FILE = "/home/krishna/costs.csv"
ACCOUNT_ID = "varsityedu"   # change later if needed

# Read CSV (handle BOM + quotes)
df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")

# Rename first column to usage_date
df.rename(columns={df.columns[0]: "usage_date"}, inplace=True)

# Remove "Service total" row
df = df[df["usage_date"] != "Service total"]

# Convert usage_date to date
df["usage_date"] = pd.to_datetime(df["usage_date"], errors="coerce")

# Melt wide → long format
df_melted = df.melt(
    id_vars=["usage_date"],
    var_name="service",
    value_name="cost"
)

# Clean service names (remove ($))
df_melted["service"] = (
    df_melted["service"]
    .str.replace(r"\(\$\)", "", regex=True)
    .str.strip()
)

# Convert cost to numeric, drop empty/zero
df_melted["cost"] = pd.to_numeric(df_melted["cost"], errors="coerce")
df_melted = df_melted.dropna(subset=["cost"])
df_melted = df_melted[df_melted["cost"] > 0]

db = SessionLocal()

for _, row in df_melted.iterrows():
    db.execute(
        text("""
            INSERT INTO aws_cost_daily (usage_date, account_id, service, cost)
            VALUES (:usage_date, :account_id, :service, :cost)
        """),
        {
            "usage_date": row["usage_date"].date(),
            "account_id": ACCOUNT_ID,
            "service": row["service"],
            "cost": float(row["cost"])
        }
    )

db.commit()
db.close()

print("AWS cost CSV imported successfully (normalized)")

