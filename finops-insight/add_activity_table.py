from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from app.database import engine
from datetime import datetime

Base = declarative_base()

class AwsActivity(Base):
    __tablename__ = "aws_activity"

    id = Column(Integer, primary_key=True)
    event_time = Column(DateTime)
    service = Column(String(100))
    event_name = Column(String(100))
    username = Column(String(100))
    source_ip = Column(String(50))

Base.metadata.create_all(bind=engine)
print("aws_activity table created")
