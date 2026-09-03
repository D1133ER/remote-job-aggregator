"""Add per-user hidden jobs

Revision ID: 003
Revises: 002
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "hidden_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("job_id", sa.String(36), sa.ForeignKey("jobs.id"), nullable=False),
        sa.UniqueConstraint("user_id", "job_id", name="uq_hidden_jobs_user_job"),
    )
    op.create_index("ix_hidden_jobs_user_id", "hidden_jobs", ["user_id"])
    op.create_index("ix_hidden_jobs_job_id", "hidden_jobs", ["job_id"])


def downgrade() -> None:
    op.drop_table("hidden_jobs")