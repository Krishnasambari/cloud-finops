from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.database import SessionLocal


def normalize_csv(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df = df.rename(columns={df.columns[0]: "usage_date"})
    df = df[df["usage_date"] != "Service total"]
    df["usage_date"] = pd.to_datetime(df["usage_date"], errors="coerce")
    df = df.dropna(subset=["usage_date"])

    melted = df.melt(id_vars=["usage_date"], var_name="service", value_name="cost")
    melted["service"] = melted["service"].str.replace(r"\(\$\)", "", regex=True).str.strip()
    melted["cost"] = pd.to_numeric(melted["cost"], errors="coerce")
    melted = melted.dropna(subset=["cost"])
    return melted[melted["cost"] > 0]


def import_rows(csv_path: Path, account_id: str) -> int:
    rows = normalize_csv(csv_path)
    db = SessionLocal()
    try:
        for _, row in rows.iterrows():
            db.execute(
                text(
                    """
                    INSERT INTO aws_cost_daily (usage_date, account_id, service, cost)
                    VALUES (:usage_date, :account_id, :service, :cost)
                    ON CONFLICT (usage_date, account_id, service)
                    DO UPDATE SET cost = EXCLUDED.cost
                    """
                ),
                {
                    "usage_date": row["usage_date"].date(),
                    "account_id": account_id,
                    "service": row["service"],
                    "cost": float(row["cost"]),
                },
            )
        db.commit()
        return len(rows)
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import normalized AWS costs CSV")
    parser.add_argument("--csv", required=True, help="Path to source CSV file")
    parser.add_argument("--account-id", default="default-account", help="Account id to store in DB")
    args = parser.parse_args()

    count = import_rows(csv_path=Path(args.csv), account_id=args.account_id)
    print(f"Imported {count} rows from {args.csv}")


if __name__ == "__main__":
    main()
