"""add_comparison_model

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-28 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'comparisons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False, index=True),
        sa.Column('analysis_a_id', sa.Integer(), sa.ForeignKey('analyses.id'), nullable=False),
        sa.Column('analysis_b_id', sa.Integer(), sa.ForeignKey('analyses.id'), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('comparison_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_comparisons_id', 'comparisons', ['id'])


def downgrade() -> None:
    op.drop_index('ix_comparisons_id', table_name='comparisons')
    op.drop_table('comparisons')
