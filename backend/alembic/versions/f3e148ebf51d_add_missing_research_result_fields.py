"""
add missing research result fields

Revision ID: f3e148ebf51d
Revises: 43b7773c0945
Create Date: 2026-09-03 22:29:29.387603
"""

from typing import Sequence, Union

revision: str = "f3e148ebf51d"
down_revision: Union[str, Sequence[str], None] = "43b7773c0945"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    No schema changes are required here.

    Revision 43b7773c0945 already creates the research_results
    fields and unique constraint that this migration previously
    attempted to add again.
    """
    pass


def downgrade() -> None:
    """No schema changes to reverse."""
    pass