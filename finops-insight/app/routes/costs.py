from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AwsCostDaily

router = APIRouter(tags=["costs"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/costs")
def get_costs(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(AwsCostDaily)

    if start_date:
        query = query.filter(AwsCostDaily.usage_date >= start_date)
    if end_date:
        query = query.filter(AwsCostDaily.usage_date <= end_date)

    rows = query.order_by(AwsCostDaily.usage_date.asc()).all()
    return [
        {
            "id": row.id,
            "date": row.usage_date.isoformat(),
            "account_id": row.account_id,
            "service": row.service,
            "cost": float(row.cost),
        }
        for row in rows
    ]


@router.get("/costs/daily")
def daily_costs(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(
        AwsCostDaily.usage_date,
        func.sum(AwsCostDaily.cost).label("total_cost"),
    )
    if start_date:
        query = query.filter(AwsCostDaily.usage_date >= start_date)
    if end_date:
        query = query.filter(AwsCostDaily.usage_date <= end_date)

    rows = (
        query.group_by(AwsCostDaily.usage_date)
        .order_by(AwsCostDaily.usage_date.asc())
        .all()
    )
    return [{"date": usage_date.isoformat(), "total_cost": float(cost)} for usage_date, cost in rows]


@router.get("/costs/by-service")
def cost_by_service(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(
        AwsCostDaily.usage_date,
        AwsCostDaily.service,
        func.sum(AwsCostDaily.cost).label("cost"),
    ).filter(AwsCostDaily.service != "Total costs")

    if start_date:
        query = query.filter(AwsCostDaily.usage_date >= start_date)
    if end_date:
        query = query.filter(AwsCostDaily.usage_date <= end_date)

    rows = (
        query.group_by(AwsCostDaily.usage_date, AwsCostDaily.service)
        .order_by(AwsCostDaily.usage_date.asc(), AwsCostDaily.service.asc())
        .all()
    )
    return [
        {"date": usage_date.isoformat(), "service": service, "cost": float(cost)}
        for usage_date, service, cost in rows
    ]


@router.get("/costs/by-service-day")
def costs_by_service_day(
    usage_date: date,
    db: Session = Depends(get_db),
):
    result = db.execute(
        text("""
            SELECT service, SUM(cost) AS cost
            FROM aws_cost_daily
            WHERE usage_date = :usage_date
              AND service <> 'Total costs'
            GROUP BY service
            ORDER BY cost DESC
        """),
        {"usage_date": usage_date},
    ).fetchall()

    return [
        {
            "service": row.service,
            "cost": float(row.cost)
        }
        for row in result
    ]


@router.get("/activity/last-24-hours")
def last_24h_activity(db: Session = Depends(get_db)):
    rows = db.execute(
        text(
            """
            SELECT event_time, service, event_name, username, source_ip
            FROM aws_activity
            ORDER BY event_time DESC
            LIMIT 50
            """
        )
    ).fetchall()

    return [
        {
            "time": str(r[0]),
            "service": r[1],
            "event": r[2],
            "user": r[3],
            "ip": r[4],
        }
        for r in rows
    ]
