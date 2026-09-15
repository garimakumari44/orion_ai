"""align research results schema

Revision ID: 43b7773c0945
Revises: 5629ca6213c7
Create Date: 2026-09-03 19:04:15.242375

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "43b7773c0945"
down_revision: Union[str, Sequence[str], None] = "5629ca6213c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Align research_results with the ResearchResult ORM model."""

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

    op.create_unique_constraint(
        "uq_research_results_research_id",
        "research_results",
        ["research_id"],
    )

    # Remove migration-time defaults after existing rows are populated.
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


def downgrade() -> None:
    """Restore the original research_results schema."""

    op.drop_constraint(
        "uq_research_results_research_id",
        "research_results",
        type_="unique",
    )

    op.drop_column("research_results", "citations")
    op.drop_column("research_results", "agent_results")
    op.drop_column("research_results", "insights")
    op.drop_column("research_results", "documents")
    op.drop_column("research_results", "evidence")
    op.drop_column("research_results", "overview")