"""add_m14_production_indexes

Revision ID: d4e5f6a7b8c0
Revises: c3d4e5f6a7b8
Create Date: 2026-07-28 23:59:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4e5f6a7b8c0'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])
    op.create_index('ix_analyses_status', 'analyses', ['status'])
    op.create_index('ix_reports_status', 'reports', ['status'])
    op.create_index('ix_reports_format', 'reports', ['format'])
    op.create_index('ix_comparisons_created_at', 'comparisons', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_comparisons_created_at', table_name='comparisons')
    op.drop_index('ix_reports_format', table_name='reports')
    op.drop_index('ix_reports_status', table_name='reports')
    op.drop_index('ix_analyses_status', table_name='analyses')
    op.drop_index('ix_projects_user_id', table_name='projects')
