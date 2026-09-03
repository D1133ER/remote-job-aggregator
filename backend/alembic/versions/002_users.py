"""Add user tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('is_premium', sa.Boolean(), nullable=True),
        sa.Column('preferred_categories', postgresql.JSON(), nullable=True),
        sa.Column('preferred_remote_types', postgresql.JSON(), nullable=True),
        sa.Column('preferred_locations', postgresql.JSON(), nullable=True),
        sa.Column('preferred_skills', postgresql.JSON(), nullable=True),
        sa.Column('salary_expectation_min', sa.Integer(), nullable=True),
        sa.Column('salary_expectation_max', sa.Integer(), nullable=True),
    )
    
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    
    # Create saved_jobs table
    op.create_table(
        'saved_jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('job_id', sa.String(36), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
    )
    
    op.create_index('ix_saved_jobs_user_id', 'saved_jobs', ['user_id'])
    op.create_index('ix_saved_jobs_job_id', 'saved_jobs', ['job_id'])
    
    # Create job_alerts table
    op.create_table(
        'job_alerts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('keywords', sa.String(500), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('remote_type', sa.String(50), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('frequency', sa.String(20), nullable=True),
    )
    
    op.create_index('ix_job_alerts_user_id', 'job_alerts', ['user_id'])
    
    # Create hidden_companies table
    op.create_table(
        'hidden_companies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('company_name', sa.String(200), nullable=False),
        sa.Column('reason', sa.String(500), nullable=True),
    )
    
    op.create_index('ix_hidden_companies_user_id', 'hidden_companies', ['user_id'])


def downgrade() -> None:
    op.drop_table('hidden_companies')
    op.drop_table('job_alerts')
    op.drop_table('saved_jobs')
    op.drop_table('users')