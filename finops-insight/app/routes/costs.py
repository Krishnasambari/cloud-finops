from datetime import date
from sqlalchemy import text
from app.database import SessionLocal
from fastapi import APIRouter

router = APIRouter()

@router.get("/costs/by-service-day")
def costs_by_service_day(date: date):
    db = SessionLocal()

    result = db.execute(
        text("""
            SELECT service, SUM(cost) AS cost
            FROM aws_cost_daily
            WHERE usage_date = :date
              AND service <> 'Total costs'
            GROUP BY service
            ORDER BY cost DESC
        """),
        {"date": date}
    ).fetchall()

    db.close()

    return [
        {
            "service": row.service,
            "cost": float(row.cost)
        }
        for row in result
    ]

