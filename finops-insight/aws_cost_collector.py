import boto3
from datetime import date, timedelta
from app.database import SessionLocal
from app.models import AwsCostDaily

ce = boto3.client("ce", region_name="us-east-1")

end = date.today()
start = end - timedelta(days=1)

response = ce.get_cost_and_usage(
    TimePeriod={
        "Start": start.strftime("%Y-%m-%d"),
        "End": end.strftime("%Y-%m-%d")
    },
    Granularity="DAILY",
    Metrics=["UnblendedCost"],
    GroupBy=[
        {"Type": "DIMENSION", "Key": "SERVICE"}
    ]
)

db = SessionLocal()

for group in response["ResultsByTime"][0]["Groups"]:
    service = group["Keys"][0]
    cost = float(group["Metrics"]["UnblendedCost"]["Amount"])

    if cost == 0:
        continue

    db.add(
        AwsCostDaily(
            date=start,
            account_id="personal-aws",
            service=service,
            cost=cost
        )
    )

db.commit()
db.close()

print("AWS cost data inserted")
