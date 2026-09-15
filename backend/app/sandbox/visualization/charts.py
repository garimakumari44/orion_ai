"""
charts.py
---------

High-level chart generation utilities.

Supported Charts
----------------
- Line Chart
- Bar Chart
- Pie Chart

Features
--------
- Accepts Pandas DataFrames
- Saves figures to disk
- Returns matplotlib Figure object
- Consistent styling
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


class ChartGenerator:
    """Utility class for generating standard charts."""

    def __init__(self, figsize=(10, 6)):
        self.figsize = figsize

    def line(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "",
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        output: Optional[str] = None,
    ):
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.plot(df[x], df[y], linewidth=2)

        ax.set_title(title)
        ax.set_xlabel(xlabel or x)
        ax.set_ylabel(ylabel or y)
        ax.grid(True)

        fig.tight_layout()

        if output:
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output, dpi=300)

        return fig

    def bar(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "",
        output: Optional[str] = None,
    ):
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.bar(df[x], df[y])

        ax.set_title(title)
        ax.set_xlabel(x)
        ax.set_ylabel(y)

        fig.tight_layout()

        if output:
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output, dpi=300)

        return fig

    def pie(
        self,
        df: pd.DataFrame,
        labels: str,
        values: str,
        title: str = "",
        autopct: str = "%1.1f%%",
        output: Optional[str] = None,
    ):
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.pie(
            df[values],
            labels=df[labels],
            autopct=autopct,
            startangle=90,
        )

        ax.set_title(title)

        fig.tight_layout()

        if output:
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output, dpi=300)

        return fig


charts = ChartGenerator()