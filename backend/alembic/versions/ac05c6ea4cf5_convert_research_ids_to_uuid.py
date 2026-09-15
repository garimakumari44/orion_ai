"""convert research ids to uuid

Revision ID: ac05c6ea4cf5
Revises: 44604377e479
Create Date: 2026-09-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# ---------------------------------------------------------------------------
# Alembic identifiers
# ---------------------------------------------------------------------------

revision: str = "ac05c6ea4cf5"
down_revision: Union[str, Sequence[str], None] = "44604377e479"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------

def upgrade() -> None:
    """
    Convert research.id from INTEGER to UUID.

    Existing relationships are preserved for:

        research_execution.research_id
        research_results.research_id
        saved_artifacts.research_id

    Existing research rows receive generated UUIDs and all existing foreign
    keys are remapped to the corresponding UUID.
    """

    # -----------------------------------------------------------------------
    # 1. Enable PostgreSQL UUID generation
    # -----------------------------------------------------------------------

    op.execute(
        "CREATE EXTENSION IF NOT EXISTS pgcrypto"
    )

    # -----------------------------------------------------------------------
    # 2. Drop all foreign keys referencing research.id
    #
    # We must do this BEFORE dropping/replacing research's primary key.
    # -----------------------------------------------------------------------

    op.drop_constraint(
        "research_execution_research_id_fkey",
        "research_execution",
        type_="foreignkey",
    )

    op.drop_constraint(
        "research_results_research_id_fkey",
        "research_results",
        type_="foreignkey",
    )

    op.drop_constraint(
        "saved_artifacts_research_id_fkey",
        "saved_artifacts",
        type_="foreignkey",
    )

    # -----------------------------------------------------------------------
    # 3. Add temporary UUID column to research
    # -----------------------------------------------------------------------

    op.add_column(
        "research",
        sa.Column(
            "id_uuid",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    # Generate one UUID for every existing research row.
    op.execute(
        """
        UPDATE research
        SET id_uuid = gen_random_uuid()
        WHERE id_uuid IS NULL
        """
    )

    # Validate migration mapping.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM research
                WHERE id_uuid IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Research UUID migration failed: NULL id_uuid found';
            END IF;
        END
        $$;
        """
    )

    # -----------------------------------------------------------------------
    # 4. Migrate research_execution.research_id
    # -----------------------------------------------------------------------

    op.add_column(
        "research_execution",
        sa.Column(
            "research_id_uuid",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE research_execution re
        SET research_id_uuid = r.id_uuid
        FROM research r
        WHERE re.research_id = r.id
        """
    )

    # Every existing research_execution row must map successfully.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM research_execution
                WHERE research_id_uuid IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Research UUID migration failed: unmapped research_execution.research_id found';
            END IF;
        END
        $$;
        """
    )

    # -----------------------------------------------------------------------
    # 5. Migrate research_results.research_id
    # -----------------------------------------------------------------------

    op.add_column(
        "research_results",
        sa.Column(
            "research_id_uuid",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE research_results rr
        SET research_id_uuid = r.id_uuid
        FROM research r
        WHERE rr.research_id = r.id
        """
    )

    # Every existing research_result row must map successfully.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM research_results
                WHERE research_id_uuid IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Research UUID migration failed: unmapped research_results.research_id found';
            END IF;
        END
        $$;
        """
    )

    # -----------------------------------------------------------------------
    # 6. Migrate saved_artifacts.research_id
    # -----------------------------------------------------------------------

    op.add_column(
        "saved_artifacts",
        sa.Column(
            "research_id_uuid",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE saved_artifacts sa
        SET research_id_uuid = r.id_uuid
        FROM research r
        WHERE sa.research_id = r.id
        """
    )

    # Every existing saved_artifact row must map successfully.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM saved_artifacts
                WHERE research_id_uuid IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Research UUID migration failed: unmapped saved_artifacts.research_id found';
            END IF;
        END
        $$;
        """
    )

    # -----------------------------------------------------------------------
    # 7. Drop indexes on old INTEGER foreign-key columns
    # -----------------------------------------------------------------------

    op.execute(
        """
        DROP INDEX IF EXISTS ix_research_execution_research_id
        """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS ix_research_results_research_id
        """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS ix_saved_artifacts_research_id
        """
    )

    # -----------------------------------------------------------------------
    # 8. Remove old INTEGER FK columns
    # -----------------------------------------------------------------------

    op.drop_column(
        "research_execution",
        "research_id",
    )

    op.drop_column(
        "research_results",
        "research_id",
    )

    op.drop_column(
        "saved_artifacts",
        "research_id",
    )

    # -----------------------------------------------------------------------
    # 9. Rename temporary UUID FK columns
    # -----------------------------------------------------------------------

    op.alter_column(
        "research_execution",
        "research_id_uuid",
        new_column_name="research_id",
    )

    op.alter_column(
        "research_results",
        "research_id_uuid",
        new_column_name="research_id",
    )

    op.alter_column(
        "saved_artifacts",
        "research_id_uuid",
        new_column_name="research_id",
    )

    # -----------------------------------------------------------------------
    # 10. Drop old research primary key
    #
    # All dependent foreign keys have already been removed above.
    # -----------------------------------------------------------------------

    op.drop_constraint(
        "research_pkey",
        "research",
        type_="primary",
    )

    # -----------------------------------------------------------------------
    # 11. Drop old INTEGER research.id
    # -----------------------------------------------------------------------

    op.drop_column(
        "research",
        "id",
    )

    # -----------------------------------------------------------------------
    # 12. Rename UUID id column
    # -----------------------------------------------------------------------

    op.alter_column(
        "research",
        "id_uuid",
        new_column_name="id",
    )

    # -----------------------------------------------------------------------
    # 13. Make research.id a UUID primary key
    # -----------------------------------------------------------------------

    op.alter_column(
        "research",
        "id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
        server_default=sa.text("gen_random_uuid()"),
    )

    op.create_primary_key(
        "research_pkey",
        "research",
        ["id"],
    )

    # -----------------------------------------------------------------------
    # 14. Recreate indexes
    # -----------------------------------------------------------------------

    op.create_index(
        "ix_research_id",
        "research",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_research_execution_research_id",
        "research_execution",
        ["research_id"],
        unique=False,
    )

    op.create_index(
        "ix_research_results_research_id",
        "research_results",
        ["research_id"],
        unique=False,
    )

    op.create_index(
        "ix_saved_artifacts_research_id",
        "saved_artifacts",
        ["research_id"],
        unique=False,
    )

    # -----------------------------------------------------------------------
    # 15. Recreate foreign keys against UUID research.id
    # -----------------------------------------------------------------------

    op.create_foreign_key(
        "research_execution_research_id_fkey",
        "research_execution",
        "research",
        ["research_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "research_results_research_id_fkey",
        "research_results",
        "research",
        ["research_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "saved_artifacts_research_id_fkey",
        "saved_artifacts",
        "research",
        ["research_id"],
        ["id"],
        ondelete="CASCADE",
    )


# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------

def downgrade() -> None:
    """
    UUID -> INTEGER downgrade is intentionally unsupported.

    The migration generates new UUIDs for existing research rows, so there
    is no deterministic way to reconstruct the original integer IDs.

    Use a database backup to restore the previous schema/data.
    """

    raise RuntimeError(
        "Downgrade from UUID research IDs to INTEGER is not supported. "
        "Restore the database from a backup to reverse this migration."
    )