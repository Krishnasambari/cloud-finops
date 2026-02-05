from app.database import SessionLocal
from app.models import AwsCostDaily
from datetime import date

db = SessionLocal()

row = AwsCostDaily(
    date=date(2026, 1, 21),
    account_id="111111111111",
    service="EC2",
    cost=25.50
)

db.add(row)
db.commit()
db.close()

print("Sample data inserted")
