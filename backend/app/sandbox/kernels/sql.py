"""
SQL execution kernel.

Supports:
- SQLite (default)
- PostgreSQL (optional)
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import psycopg
except ImportError:
    psycopg = None


class SQLKernel:
    """
    SQL execution kernel.

    Examples:
        kernel = SQLKernel("sqlite")

        kernel.execute("CREATE TABLE users(id INTEGER);")
        kernel.execute("INSERT INTO users VALUES (1);")
        result = kernel.execute("SELECT * FROM users;")
    """

    language = "sql"

    def __init__(
        self,
        backend: str = "sqlite",
        database: str = ":memory:",
        **connection_kwargs,
    ):
        self.backend = backend.lower()

        if self.backend == "sqlite":
            self.connection = sqlite3.connect(database)
            self.connection.row_factory = sqlite3.Row

        elif self.backend == "postgres":
            if psycopg is None:
                raise ImportError(
                    "psycopg must be installed for PostgreSQL support."
                )

            self.connection = psycopg.connect(
                dbname=database,
                **connection_kwargs,
            )

        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def execute(self, query: str) -> Dict[str, Any]:
        cursor = self.connection.cursor()

        try:
            cursor.execute(query)

            if cursor.description:
                columns = [c[0] for c in cursor.description]
                rows = cursor.fetchall()

                data = [
                    dict(zip(columns, row))
                    for row in rows
                ]
            else:
                self.connection.commit()
                data = []

            return {
                "success": True,
                "language": self.language,
                "rows": data,
                "rowcount": cursor.rowcount,
            }

        except Exception as exc:
            self.connection.rollback()

            return {
                "success": False,
                "language": self.language,
                "error": str(exc),
            }

    def close(self):
        self.connection.close()