"""Add return_percent column to backtests table

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add return_percent column if it doesn't exist
    op.add_column('backtests', sa.Column('return_percent', sa.Float(), nullable=True))


def downgrade() -> None:
    # Remove return_percent column
    op.drop_column('backtests', 'return_percent')
