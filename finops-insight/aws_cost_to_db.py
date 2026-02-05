import boto3
import psycopg2
from datetime import datetime, timedelta, timezone

# AWS Cost Explorer (must be us-east-1)
ce = boto3.client("ce", region_name="us-east-1")

# PostgreSQL connection
conn = psycopg2.connect(
    host="localhost",
    database="finops",
    user="awsuser",
    password="Krishna@098",
    port=5432
)
cur = conn.cursor()

# Date range (last 24h)
end = datetime.now(timezone.utc).date()
start = end - timedelta(days=1)

response = ce.get_cost_and_usage(
    TimePeriod={
        "Start": start.strftime("%Y-%m-%d"),
        "End": end.strftime("%Y-%m-%d"),
    },
    Granularity="DAILY",
    Metrics=["UnblendedCost"],
    GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
)

print("📊 Saving AWS costs to DB:")

for group in response["ResultsByTime"][0]["Groups"]:
    service = group["Keys"][0]
    cost = float(group["Metrics"]["UnblendedCost"]["Amount"])

    if cost > 0:
        print(f"{service}: ${cost:.4f}")
        cur.execute(
            """
            INSERT INTO aws_daily_costs
            (service_name, cost, usage_date)
            VALUES (%s, %s, %s)
            """,
            (service, cost, start),
        )

conn.commit()
cur.close()
conn.close()

print("✅ AWS cost data saved successfully")

