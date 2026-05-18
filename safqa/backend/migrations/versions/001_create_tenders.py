"""create tenders table

Revision ID: 001_create_tenders
Revises:
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa


revision = "001_create_tenders"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "tenders",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("reference_number", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("authority", sa.Text(), nullable=False),
        sa.Column("city", sa.Text(), nullable=True),
        sa.Column("domain_code", sa.Text(), nullable=False),
        sa.Column("domain_label", sa.Text(), nullable=True),
        sa.Column("procedure_type", sa.Text(), nullable=True),
        sa.Column("budget_raw", sa.Text(), nullable=True),
        sa.Column("budget_mad", sa.Numeric(15, 2), nullable=True),
        sa.Column("published_at", sa.Date(), nullable=False),
        sa.Column("deadline_at", sa.Date(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'active'")),
        sa.Column("scraped_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_tenders_ref", "tenders", ["reference_number"], unique=True)
    op.create_index(
        "idx_tenders_domain_dl",
        "tenders",
        ["domain_code", "deadline_at"],
        unique=False,
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index(
        "idx_tenders_deadline",
        "tenders",
        ["deadline_at"],
        unique=False,
        postgresql_where=sa.text("status = 'active'"),
    )
    op.execute(
        "CREATE INDEX idx_tenders_fts ON tenders "
        "USING GIN (to_tsvector('french', coalesce(title,'') || ' ' || coalesce(authority,'')))"
    )


def downgrade() -> None:
    op.drop_index("idx_tenders_fts", table_name="tenders")
    op.drop_index("idx_tenders_deadline", table_name="tenders")
    op.drop_index("idx_tenders_domain_dl", table_name="tenders")
    op.drop_index("idx_tenders_ref", table_name="tenders")
    op.drop_table("tenders")
