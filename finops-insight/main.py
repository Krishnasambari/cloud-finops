from fastapi import FastAPI, Query
from app.database import SessionLocal
from app.models import AwsCostDaily
from datetime import date
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/costs")
def get_costs(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None)
):
    db = SessionLocal()
    query = db.query(AwsCostDaily)

    if start_date:
        query = query.filter(AwsCostDaily.usage_date >= start_date)
    if end_date:
        query = query.filter(AwsCostDaily.usagge_date <= end_date)

    data = query.all()
    db.close()
    return data


@app.get("/costs/daily")
def daily_costs():
    db = SessionLocal()
    data = (
        db.query(
            AwsCostDaily.usage_date,
            func.sum(AwsCostDaily.cost).label("total_cost")
        )
        .group_by(AwsCostDaily.usage_date)
        .order_by(AwsCostDaily.usage_date)
        .all()
    )
    db.close()

    return [
        {"date": d, "total_cost": float(c)}
        for d, c in data
    ]


@app.get("/costs/by-service")
def cost_by_service():
    db = SessionLocal()
    data = (
        db.query(
            AwsCostDaily.service,
            func.sum(AwsCostDaily.cost).label("cost")
        )
        .group_by(AwsCostDaily.service)
        .all()
    )
    db.close()

    return [
        {"service": s, "cost": float(c),"date": d }
        for s, c, d in data
    ]


@app.get("/costs/by-service-day")
def cost_by_service_day(date: date):
    db = SessionLocal()

    data = (
        db.query(
            AwsCostDaily.service,
            func.sum(AwsCostDaily.cost).label("cost")
        )
        .filter(
            AwsCostDaily.usage_date == date,
            AwsCostDaily.service != "Total costs"
        )
        .group_by(AwsCostDaily.service)
        .order_by(func.sum(AwsCostDaily.cost).desc())
        .all()
    )

    db.close()

    result = []

    for service, cost in rows:
        result.append({
            "service": service,
             "cost": float(cost)
          })

from sqlalchemy import text

@app.get("/activity/last-24-hours")
def last_24h_activity():
    db = SessionLocal()
    rows = db.execute(
        text("""
            SELECT event_time, service, event_name, username, source_ip
            FROM aws_activity
            ORDER BY event_time DESC
            LIMIT 50
        """)
    ).fetchall()
    db.close()

    return [
        {
            "time": str(r[0]),
            "service": r[1],
            "event": r[2],
            "user": r[3],
            "ip": r[4]
        }
        for r in rows
    ]
