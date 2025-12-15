"""Add votes field to Game

Revision ID: 002
Revises: 001
Create Date: 2024-12-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add votes column to games table
    op.add_column('games', sa.Column('votes', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    # Set default value for existing rows
    op.execute("UPDATE games SET votes = '{}'")


def downgrade() -> None:
    # Remove votes column
    op.drop_column('games', 'votes')
