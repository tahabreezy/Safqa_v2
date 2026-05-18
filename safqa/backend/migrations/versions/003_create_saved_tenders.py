"""create saved_tenders table

Revision ID: 003_create_saved_tenders
Revises: 002_create_users
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa


revision = "003_create_saved_tenders"
down_revision = "002_create_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "saved_tenders",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("tender_id", sa.UUID(), nullable=False),
        sa.Column("saved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tender_id"], ["tenders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "tender_id"),
    )


def downgrade() -> None:
    op.drop_table("saved_tenders")
