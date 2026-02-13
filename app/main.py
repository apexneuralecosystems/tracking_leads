"""
ApexNeural tracking microservice — FastAPI app entrypoint.

Run with: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import events, leads, tracking

settings = get_settings()

# Configure logging so production and local runs have consistent output
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)

app = FastAPI(
    title=settings.app_name,
    description="Lead tracking: GET /go/{campaign_name}/{tracking_id} records click and redirects. Events stored in UTC.",
)

# CORS: from env CORS_ORIGINS ("*" or comma-separated list)
_origins = ["*"]
if getattr(settings, "cors_origins", "*") and settings.cors_origins.strip() != "*":
    _origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(tracking.router, tags=["tracking"])
app.include_router(events.router, tags=["events"])
app.include_router(leads.router, tags=["leads"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
