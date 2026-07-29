"""add_analysis_warnings_table

Revision ID: cd173a67ae96
Revises: 3f88aa8a120f
Create Date: 2026-07-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'cd173a67ae96'
down_revision: Union[str, None] = '3f88aa8a120f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('analysis_warnings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('detector_name', sa.String(length=64), nullable=False),
        sa.Column('message', sa.String(length=1024), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_warnings_id'), 'analysis_warnings', ['id'], unique=False)
    op.create_index(op.f('ix_analysis_warnings_analysis_id'), 'analysis_warnings', ['analysis_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_analysis_warnings_analysis_id'), table_name='analysis_warnings')
    op.drop_index(op.f('ix_analysis_warnings_id'), table_name='analysis_warnings')
    op.drop_table('analysis_warnings')
