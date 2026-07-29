"""add_m54_covering_indexes

Revision ID: a1b2c3d4e5f6
Revises: cd173a67ae96
Create Date: 2026-07-26 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'cd173a67ae96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_analysis_files_language', 'analysis_files', ['analysis_id', 'language'], unique=False)
    op.create_index('ix_analysis_files_is_directory', 'analysis_files', ['analysis_id', 'is_directory'], unique=False)
    op.create_index('ix_analysis_warnings_detector', 'analysis_warnings', ['analysis_id', 'detector_name'], unique=False)
    op.create_index('ix_dependencies_type', 'dependencies', ['analysis_id', 'type'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_analysis_files_language', table_name='analysis_files')
    op.drop_index('ix_analysis_files_is_directory', table_name='analysis_files')
    op.drop_index('ix_analysis_warnings_detector', table_name='analysis_warnings')
    op.drop_index('ix_dependencies_type', table_name='dependencies')
