"""add figi to companies

Revision ID: 84e065750332
Revises: ac05c6ea4cf5
Create Date: 2026-09-19 09:20:55.323720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84e065750332'
down_revision: Union[str, Sequence[str], None] = 'ac05c6ea4cf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "companies",
        sa.Column("figi", sa.String(length=50), nullable=True),
    )

    op.create_index(
        "ix_companies_figi",
        "companies",
        ["figi"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_companies_figi",
        table_name="companies",
    )

    op.drop_column(
        "companies",
        "figi",
    )