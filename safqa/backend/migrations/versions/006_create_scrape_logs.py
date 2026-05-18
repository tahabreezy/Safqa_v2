"""create scrape_logs table

Revision ID: 006_create_scrape_logs
Revises: 005_create_alert_notifications
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "006_create_scrape_logs"
down_revision = "005_create_alert_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scrape_logs",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("domain_code", sa.Text(), nullable=False),
        sa.Column("count_scraped", sa.Integer(), nullable=False),
        sa.Column("count_upserted", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("errors", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("run_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("scrape_logs")
