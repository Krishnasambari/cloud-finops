from __future__ import annotations

from datetime import datetime, timedelta, timezone

import boto3
from sqlalchemy import text

from app.database import SessionLocal


def collect_recent_activity(hours: int = 24, limit: int = 50) -> list[dict[str, str | datetime]]:
    client = boto3.client("cloudtrail")
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)

    response = client.lookup_events(
        StartTime=start_time,
        EndTime=end_time,
        MaxResults=limit,
    )

    rows: list[dict[str, str | datetime]] = []
    for event in response.get("Events", []):
        rows.append(
            {
                "event_time": event["EventTime"],
                "service": event["EventSource"],
                "event_name": event["EventName"],
                "username": event.get("Username", "Unknown"),
                "source_ip": event.get("SourceIPAddress", "N/A"),
            }
        )
    return rows


def save_activity(rows: list[dict[str, str | datetime]]) -> int:
    db = SessionLocal()
    try:
        for row in rows:
            db.execute(
                text(
                    """
                    INSERT INTO aws_activity (event_time, service, event_name, username, source_ip)
                    VALUES (:event_time, :service, :event_name, :username, :source_ip)
                    """
                ),
                row,
            )
        db.commit()
        return len(rows)
    finally:
        db.close()


def main() -> None:
    rows = collect_recent_activity()
    count = save_activity(rows)
    print(f"Saved {count} CloudTrail activity rows")


if __name__ == "__main__":
    main()
