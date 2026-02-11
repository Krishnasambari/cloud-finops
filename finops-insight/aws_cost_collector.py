from __future__ import annotations

import os
from datetime import date, timedelta

import boto3
from sqlalchemy import text

from app.database import SessionLocal

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ACCOUNT_ID = os.getenv("FINOPS_ACCOUNT_ID", "default-account")


def collect_daily_costs(start_date: date, end_date: date) -> list[dict[str, float | str]]:
    client = boto3.client("ce", region_name=AWS_REGION)
    response = client.get_cost_and_usage(
        TimePeriod={
            "Start": start_date.strftime("%Y-%m-%d"),
            "End": end_date.strftime("%Y-%m-%d"),
        },
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    groups = response.get("ResultsByTime", [{}])[0].get("Groups", [])
    data: list[dict[str, float | str]] = []
    for group in groups:
        service = group["Keys"][0]
        cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
        if cost <= 0:
            continue
        data.append({"service": service, "cost": cost})
    return data


def save_costs(usage_date: date, rows: list[dict[str, float | str]]) -> int:
    db = SessionLocal()
    try:
        for row in rows:
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
                    "usage_date": usage_date,
                    "account_id": ACCOUNT_ID,
                    "service": row["service"],
                    "cost": row["cost"],
                },
            )
        db.commit()
        return len(rows)
    finally:
        db.close()


def main() -> None:
    end_date = date.today()
    start_date = end_date - timedelta(days=1)
    costs = collect_daily_costs(start_date=start_date, end_date=end_date)
    count = save_costs(usage_date=start_date, rows=costs)
    print(f"Saved {count} cost rows for {start_date.isoformat()}")


if __name__ == "__main__":
    main()
