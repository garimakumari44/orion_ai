"""
exports.py
----------

Export utilities for visualizations and tabular data.

Supported Formats
-----------------
- PNG
- PDF
- SVG
- CSV
- Excel
- HTML

Features
--------
- Export matplotlib figures
- Export pandas DataFrames
- Automatic directory creation
- Simple, reusable API
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
from matplotlib.figure import Figure


class Exporter:
    """Utility class for exporting figures and tables."""

    @staticmethod
    def _prepare_path(path: str | Path) -> Path:
        """Create parent directories if necessary."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    # ------------------------------------------------------------------
    # Figure Exports
    # ------------------------------------------------------------------

    @staticmethod
    def figure(
        figure: Figure,
        path: str,
        dpi: int = 300,
        transparent: bool = False,
    ) -> Path:
        """
        Export a matplotlib figure.

        Example
        -------
        exporter.figure(fig, "reports/chart.png")
        """
        output = Exporter._prepare_path(path)

        figure.savefig(
            output,
            dpi=dpi,
            bbox_inches="tight",
            transparent=transparent,
        )

        return output

    @staticmethod
    def png(
        figure: Figure,
        path: str,
        dpi: int = 300,
    ) -> Path:
        """Export figure as PNG."""
        return Exporter.figure(figure, path, dpi=dpi)

    @staticmethod
    def pdf(
        figure: Figure,
        path: str,
    ) -> Path:
        """Export figure as PDF."""
        return Exporter.figure(figure, path)

    @staticmethod
    def svg(
        figure: Figure,
        path: str,
    ) -> Path:
        """Export figure as SVG."""
        return Exporter.figure(figure, path)

    # ------------------------------------------------------------------
    # DataFrame Exports
    # ------------------------------------------------------------------

    @staticmethod
    def csv(
        df: pd.DataFrame,
        path: str,
        index: bool = False,
    ) -> Path:
        """Export DataFrame to CSV."""
        output = Exporter._prepare_path(path)
        df.to_csv(output, index=index)
        return output

    @staticmethod
    def excel(
        df: pd.DataFrame,
        path: str,
        sheet_name: str = "Sheet1",
        index: bool = False,
    ) -> Path:
        """Export DataFrame to Excel."""
        output = Exporter._prepare_path(path)

        with pd.ExcelWriter(output) as writer:
            df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=index,
            )

        return output

    @staticmethod
    def html(
        df: pd.DataFrame,
        path: str,
        index: bool = False,
    ) -> Path:
        """Export DataFrame as an HTML table."""
        output = Exporter._prepare_path(path)

        df.to_html(output, index=index)

        return output

    @staticmethod
    def markdown(
        df: pd.DataFrame,
        path: str,
        index: bool = False,
    ) -> Path:
        """Export DataFrame as Markdown."""
        output = Exporter._prepare_path(path)

        output.write_text(
            df.to_markdown(index=index),
            encoding="utf-8",
        )

        return output


# Singleton instance
exporter = Exporter()