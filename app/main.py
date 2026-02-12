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
    description="Minimal email engagement: open pixel GET /o/{id}.png, click link GET /t/{id} → redirect. Events stored in UTC.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tracking.router, tags=["tracking"])
app.include_router(events.router, tags=["events"])
app.include_router(leads.router, tags=["leads"])


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
