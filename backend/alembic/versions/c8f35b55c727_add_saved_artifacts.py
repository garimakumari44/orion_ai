"""add saved artifacts

Revision ID: c8f35b55c727
Revises: f3e148ebf51d
Create Date: 2026-09-04 23:14:29.298667

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c8f35b55c727"
down_revision: Union[str, Sequence[str], None] = "f3e148ebf51d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. Create PostgreSQL enum if it does not already exist
    # ---------------------------------------------------------
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'save_destination'
            ) THEN
                CREATE TYPE save_destination AS ENUM (
                    'library',
                    'research',
                    'reports'
                );
            END IF;
        END
        $$;
        """
    )

    # ---------------------------------------------------------
    # 2. Reuse the existing PostgreSQL enum
    # ---------------------------------------------------------
    save_destination = postgresql.ENUM(
        "library",
        "research",
        "reports",
        name="save_destination",
        create_type=False,
    )

    # ---------------------------------------------------------
    # 3. Create saved_artifacts table
    # ---------------------------------------------------------
    op.create_table(
        "saved_artifacts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "research_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "destination",
            save_destination,
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["research_id"],
            ["research.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ---------------------------------------------------------
    # 4. Indexes
    # ---------------------------------------------------------
    op.create_index(
        "ix_saved_artifacts_destination",
        "saved_artifacts",
        ["destination"],
        unique=False,
    )

    op.create_index(
        "ix_saved_artifacts_research_id",
        "saved_artifacts",
        ["research_id"],
        unique=False,
    )


def downgrade() -> None:
    # Remove indexes
    op.drop_index(
        "ix_saved_artifacts_research_id",
        table_name="saved_artifacts",
    )

    op.drop_index(
        "ix_saved_artifacts_destination",
        table_name="saved_artifacts",
    )

    # Remove table
    op.drop_table("saved_artifacts")

    # Do NOT drop save_destination here.
    #
    # The enum may have existed before this migration,
    # so this migration does not own its lifecycle.