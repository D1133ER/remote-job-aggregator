"""Add job performance indexes to match the current model

Revision ID: 004
Revises: 003
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Single-column indexes declared via index=True in the Job model
    op.create_index("ix_jobs_remote_type", "jobs", ["remote_type"])
    op.create_index("ix_jobs_experience_level", "jobs", ["experience_level"])
    op.create_index("ix_jobs_category", "jobs", ["category"])
    op.create_index("ix_jobs_is_active", "jobs", ["is_active"])
    op.create_index("ix_jobs_posted_at", "jobs", ["posted_at"])

    # Composite indexes for common filtering/query patterns
    op.create_index("ix_jobs_active_posted", "jobs", ["is_active", "posted_at"])
    op.create_index("ix_jobs_category_remote", "jobs", ["category", "remote_type"])
    op.create_index("ix_jobs_experience_remote", "jobs", ["experience_level", "remote_type"])


def downgrade() -> None:
    op.drop_index("ix_jobs_experience_remote", table_name="jobs")
    op.drop_index("ix_jobs_category_remote", table_name="jobs")
    op.drop_index("ix_jobs_active_posted", table_name="jobs")
    op.drop_index("ix_jobs_posted_at", table_name="jobs")
    op.drop_index("ix_jobs_is_active", table_name="jobs")
    op.drop_index("ix_jobs_category", table_name="jobs")
    op.drop_index("ix_jobs_experience_level", table_name="jobs")
    op.drop_index("ix_jobs_remote_type", table_name="jobs")
