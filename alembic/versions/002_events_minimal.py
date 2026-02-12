"""events minimal: drop ip_address, user_agent, metadata

Revision ID: 002
Revises: 001
Create Date: 2026-02-05

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for col in ("metadata", "user_agent", "ip_address"):
        op.execute(sa.text(f"ALTER TABLE events DROP COLUMN IF EXISTS {col}"))


def downgrade() -> None:
    op.add_column("events", sa.Column("ip_address", sa.String(45), nullable=True))
    op.add_column("events", sa.Column("user_agent", sa.Text(), nullable=True))
    op.add_column("events", sa.Column("metadata", sa.dialects.postgresql.JSONB(), nullable=True))
