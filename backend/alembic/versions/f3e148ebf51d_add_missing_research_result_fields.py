
"""
add missing research result fields

Revision ID: f3e148ebf51d
Revises: 43b7773c0945
Create Date: 2026-09-03 22:29:29.387603

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# ============================================================
# Revision identifiers
# ============================================================

revision: str = "f3e148ebf51d"
down_revision: Union[str, Sequence[str], None] = "43b7773c0945"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ============================================================
# Upgrade
# ============================================================

def upgrade() -> None:
    """
    Bring research_results in line with the ResearchResult ORM model.

    The previous migration 43b7773c0945 was already marked as applied
    before its schema changes were physically present in the database.

    This migration therefore applies the missing changes from the
    current database state.
    """

    # --------------------------------------------------------
    # JSON research result fields
    # --------------------------------------------------------

    op.add_column(
        "research_results",
        sa.Column(
            "overview",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
    )

    op.add_column(
        "research_results",
        sa.Column(
            "evidence",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )

    op.add_column(
        "research_results",
        sa.Column(
            "documents",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )

    op.add_column(
        "research_results",
        sa.Column(
            "insights",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )

    op.add_column(
        "research_results",
        sa.Column(
            "agent_results",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )

    op.add_column(
        "research_results",
        sa.Column(
            "citations",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )

    # --------------------------------------------------------
    # One result per research project
    # --------------------------------------------------------

    op.create_unique_constraint(
        "uq_research_results_research_id",
        "research_results",
        ["research_id"],
    )

    # --------------------------------------------------------
    # Remove temporary defaults.
    #
    # Existing rows are populated using the migration-time
    # defaults above. New application rows use SQLAlchemy's
    # Python-side defaults defined by the ORM model.
    # --------------------------------------------------------

    op.alter_column(
        "research_results",
        "overview",
        server_default=None,
    )

    op.alter_column(
        "research_results",
        "evidence",
        server_default=None,
    )

    op.alter_column(
        "research_results",
        "documents",
        server_default=None,
    )

    op.alter_column(
        "research_results",
        "insights",
        server_default=None,
    )

    op.alter_column(
        "research_results",
        "agent_results",
        server_default=None,
    )

    op.alter_column(
        "research_results",
        "citations",
        server_default=None,
    )


# ============================================================
# Downgrade
# ============================================================

def downgrade() -> None:
    """
    Remove the research result fields added by this migration.
    """

    op.drop_constraint(
        "uq_research_results_research_id",
        "research_results",
        type_="unique",
    )

    op.drop_column(
        "research_results",
        "citations",
    )

    op.drop_column(
        "research_results",
        "agent_results",
    )

    op.drop_column(
        "research_results",
        "insights",
    )

    op.drop_column(
        "research_results",
        "documents",
    )

    op.drop_column(
        "research_results",
        "evidence",
    )

    op.drop_column(
        "research_results",
        "overview",
    )

