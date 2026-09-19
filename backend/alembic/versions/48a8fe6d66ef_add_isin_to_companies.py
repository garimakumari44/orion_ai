"""add isin to companies

Revision ID: 48a8fe6d66ef
Revises: 84e065750332
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "48a8fe6d66ef"
down_revision: Union[str, Sequence[str], None] = "84e065750332"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("isin", sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("companies", "isin")
