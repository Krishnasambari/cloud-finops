from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.costs import router as costs_router

app = FastAPI(title="FinOps Insight API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(costs_router)
