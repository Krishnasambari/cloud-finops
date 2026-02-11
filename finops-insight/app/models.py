from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AwsCostDaily(Base):
    __tablename__ = "aws_cost_daily"
    __table_args__ = (
        UniqueConstraint("usage_date", "account_id", "service", name="uq_cost_day_account_service"),
    )

    id = Column(Integer, primary_key=True)
    usage_date = Column(Date, nullable=False)
    account_id = Column(String(20), nullable=False)
    service = Column(String(100), nullable=False)
    cost = Column(Numeric(12, 4), nullable=False)


class AwsActivity(Base):
    __tablename__ = "aws_activity"

    id = Column(Integer, primary_key=True)
    event_time = Column(DateTime, nullable=False)
    service = Column(String(120), nullable=False)
    event_name = Column(String(120), nullable=False)
    username = Column(String(120), nullable=False)
    source_ip = Column(String(60), nullable=False)
