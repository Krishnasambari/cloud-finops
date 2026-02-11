from app.database import SessionLocal
from app.models import AwsCostDaily
from datetime import date


def main() -> None:
    db = SessionLocal()
    try:
        row = AwsCostDaily(
            usage_date=date.today(),
            account_id="111111111111",
            service="AmazonEC2",
            cost=25.50,
        )
        db.add(row)
        db.commit()
        print("Sample data inserted")
    finally:
        db.close()


if __name__ == "__main__":
    main()
