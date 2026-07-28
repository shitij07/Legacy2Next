"""add_report_model_fields

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-28 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('reports', sa.Column('analysis_id', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('reports', sa.Column('user_id', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('reports', sa.Column('title', sa.String(255), nullable=False, server_default='Report'))
    op.add_column('reports', sa.Column('format', sa.Enum('MARKDOWN', 'JSON', name='reportformat'), nullable=False, server_default='MARKDOWN'))
    op.add_column('reports', sa.Column('status', sa.Enum('GENERATING', 'READY', 'FAILED', name='reportstatus'), nullable=False, server_default='GENERATING'))
    op.add_column('reports', sa.Column('content', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('file_path', sa.String(512), nullable=True))
    op.add_column('reports', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))

    op.create_foreign_key('fk_reports_analysis_id', 'reports', 'analyses', ['analysis_id'], ['analyses.id'])
    op.create_foreign_key('fk_reports_user_id', 'reports', 'users', ['user_id'], ['users.id'])
    op.create_index(op.f('ix_reports_project_id'), 'reports', ['project_id'], unique=False)
    op.create_index(op.f('ix_reports_analysis_id'), 'reports', ['analysis_id'], unique=False)
    op.create_index(op.f('ix_reports_user_id'), 'reports', ['user_id'], unique=False)

    op.alter_column('reports', 'analysis_id', server_default=None)
    op.alter_column('reports', 'user_id', server_default=None)
    op.alter_column('reports', 'title', server_default=None)
    op.alter_column('reports', 'format', server_default=None)
    op.alter_column('reports', 'status', server_default=None)


def downgrade() -> None:
    op.drop_index(op.f('ix_reports_user_id'), table_name='reports')
    op.drop_index(op.f('ix_reports_analysis_id'), table_name='reports')
    op.drop_index(op.f('ix_reports_project_id'), table_name='reports')
    op.drop_constraint('fk_reports_user_id', 'reports', type_='foreignkey')
    op.drop_constraint('fk_reports_analysis_id', 'reports', type_='foreignkey')
    op.drop_column('reports', 'updated_at')
    op.drop_column('reports', 'file_path')
    op.drop_column('reports', 'content')
    op.drop_column('reports', 'status')
    op.drop_column('reports', 'format')
    op.drop_column('reports', 'title')
    op.drop_column('reports', 'user_id')
    op.drop_column('reports', 'analysis_id')

    sa.Enum(name='reportformat').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='reportstatus').drop(op.get_bind(), checkfirst=True)
