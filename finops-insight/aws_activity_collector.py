import boto3
from datetime import datetime, timedelta
from app.database import SessionLocal
from sqlalchemy import text

client = boto3.client("cloudtrail")

end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=24)

response = client.lookup_events(
    StartTime=start_time,
    EndTime=end_time,
    MaxResults=50
)

db = SessionLocal()

for event in response.get("Events", []):
    db.execute(
        text("""
            INSERT INTO aws_activity
            (event_time, service, event_name, username, source_ip)
            VALUES (:time, :service, :event, :user, :ip)
        """),
        {
            "time": event["EventTime"],
            "service": event["EventSource"],
            "event": event["EventName"],
            "user": event.get("Username", "Unknown"),
            "ip": event.get("SourceIPAddress", "N/A"),
        }
    )

db.commit()
db.close()

print("AWS activity data inserted")
