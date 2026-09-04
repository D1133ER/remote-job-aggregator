"""Add apply_url column to jobs

Revision ID: 005
Revises: 004
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("apply_url", sa.String(length=1000), nullable=True))
    # Backfill apply_url from source_url so existing jobs immediately have an
    # application link. Future scrapes will set the dedicated apply_url.
    op.execute("UPDATE jobs SET apply_url = source_url WHERE apply_url IS NULL")


def downgrade() -> None:
    op.drop_column("jobs", "apply_url")
