"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('company_name', sa.String(200), nullable=False),
        sa.Column('company_logo_url', sa.String(500), nullable=True),
        sa.Column('company_website', sa.String(500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_html', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('remote_type', sa.String(50), nullable=True),
        sa.Column('geo_restrictions', postgresql.JSON(), nullable=True),
        sa.Column('timezone_requirements', sa.String(200), nullable=True),
        sa.Column('salary_min', sa.Float(), nullable=True),
        sa.Column('salary_max', sa.Float(), nullable=True),
        sa.Column('salary_currency', sa.String(10), nullable=True),
        sa.Column('salary_display', sa.String(200), nullable=True),
        sa.Column('source_url', sa.String(1000), nullable=True),
        sa.Column('source_name', sa.String(100), nullable=True),
        sa.Column('source_id', sa.String(200), nullable=True),
        sa.Column('job_type', sa.String(50), nullable=True),
        sa.Column('experience_level', sa.String(50), nullable=True),
        sa.Column('skills', postgresql.JSON(), nullable=True),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
    )
    
    # Create indexes
    op.create_index('ix_jobs_title', 'jobs', ['title'])
    op.create_index('ix_jobs_company_name', 'jobs', ['company_name'])
    op.create_index('ix_jobs_source_url', 'jobs', ['source_url'], unique=True)
    op.create_index('ix_jobs_search_vector', 'jobs', ['search_vector'], postgresql_using='gin')
    op.create_index('ix_jobs_title_company', 'jobs', ['title', 'company_name'])
    
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(200), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('remote_policy', sa.String(50), nullable=True),
        sa.Column('average_response_time', sa.String(50), nullable=True),
        sa.Column('total_jobs_posted', sa.Integer(), nullable=True),
        sa.Column('total_jobs_remote', sa.Integer(), nullable=True),
    )
    
    op.create_index('ix_companies_name', 'companies', ['name'], unique=True)


def downgrade() -> None:
    op.drop_table('companies')
    op.drop_table('jobs')