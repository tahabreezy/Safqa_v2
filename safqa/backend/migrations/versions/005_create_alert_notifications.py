"""create alert_notifications table

Revision ID: 005_create_alert_notifications
Revises: 004_create_saved_searches
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa


revision = "005_create_alert_notifications"
down_revision = "004_create_saved_searches"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alert_notifications",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("saved_search_id", sa.UUID(), nullable=False),
        sa.Column("tender_id", sa.UUID(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["saved_search_id"], ["saved_searches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tender_id"], ["tenders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("saved_search_id", "tender_id", name="uq_alert_notifications_search_tender"),
    )


def downgrade() -> None:
    op.drop_table("alert_notifications")
