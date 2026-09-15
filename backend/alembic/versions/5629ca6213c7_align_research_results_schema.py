"""align research results schema

Revision ID: 5629ca6213c7
Revises: 6f9ed2cf9a9f
Create Date: 2026-09-03 19:00:11.797327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5629ca6213c7'
down_revision: Union[str, Sequence[str], None] = '6f9ed2cf9a9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
