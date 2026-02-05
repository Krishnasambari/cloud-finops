from sqlalchemy import Column, Integer, String, Date, Numeric
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AwsCostDaily(Base):
    __tablename__ = "aws_cost_daily"

    id = Column(Integer, primary_key=True)
    usage_date = Column(Date, nullable=False)
    account_id = Column(String(20), nullable=False)
    service = Column(String(100), nullable=False)
    cost = Column(Numeric(12, 4), nullable=False)

