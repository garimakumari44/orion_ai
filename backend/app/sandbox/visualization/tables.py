"""
tables.py
---------

Utilities for displaying and exporting DataFrames.

Features
--------
- Pretty printing
- Markdown tables
- HTML tables
- CSV export
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


class TableFormatter:
    """Pretty table formatter."""

    @staticmethod
    def preview(
        df: pd.DataFrame,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Return first few rows.

        Parameters
        ----------
        rows : int
            Number of rows to preview.
        """
        return df.head(rows)

    @staticmethod
    def markdown(
        df: pd.DataFrame,
        index: bool = False,
    ) -> str:
        """
        Convert DataFrame to Markdown.
        """
        return df.to_markdown(index=index)

    @staticmethod
    def html(
        df: pd.DataFrame,
        index: bool = False,
    ) -> str:
        """
        Convert DataFrame to HTML.
        """
        return df.to_html(index=index)

    @staticmethod
    def csv(
        df: pd.DataFrame,
        path: str,
        index: bool = False,
    ):
        """
        Export DataFrame to CSV.
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(path, index=index)

    @staticmethod
    def summary(df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate summary statistics.
        """
        return df.describe(include="all")


tables = TableFormatter()