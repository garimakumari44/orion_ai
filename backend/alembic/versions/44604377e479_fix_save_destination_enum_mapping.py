"""fix save destination enum mapping

Revision ID: 44604377e479
Revises: c8f35b55c727
Create Date: 2026-09-05 19:29:36.320683

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44604377e479'
down_revision: Union[str, Sequence[str], None] = 'c8f35b55c727'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
