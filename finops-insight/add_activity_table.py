from app.database import engine
from app.models import AwsActivity


def main() -> None:
    AwsActivity.__table__.create(bind=engine, checkfirst=True)
    print("aws_activity table created")


if __name__ == "__main__":
    main()
