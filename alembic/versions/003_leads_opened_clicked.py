"""add opened_at and first_click_at to leads

Revision ID: 003
Revises: 002
Create Date: 2026-02-05

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("leads", sa.Column("first_click_at", sa.DateTime(timezone=True), nullable=True))
    # Backfill from existing events (first open/click per tracking_id)
    op.execute(
        sa.text("""
        UPDATE leads l SET opened_at = sub.min_at
        FROM (
            SELECT tracking_id, MIN(created_at) AS min_at
            FROM events WHERE event_type = 'open'
            GROUP BY tracking_id
        ) sub
        WHERE l.tracking_id = sub.tracking_id AND l.opened_at IS NULL
    """)
    )
    op.execute(
        sa.text("""
        UPDATE leads l SET first_click_at = sub.min_at
        FROM (
            SELECT tracking_id, MIN(created_at) AS min_at
            FROM events WHERE event_type = 'click'
            GROUP BY tracking_id
        ) sub
        WHERE l.tracking_id = sub.tracking_id AND l.first_click_at IS NULL
    """)
    )


def downgrade() -> None:
    op.drop_column("leads", "first_click_at")
    op.drop_column("leads", "opened_at")
