"""
plots.py
--------

Statistical plotting utilities.

Supported
---------
- Scatter Plot
- Histogram

Designed for exploratory data analysis.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


class PlotGenerator:
    """Statistical plotting helper."""

    def __init__(self, figsize=(10, 6)):
        self.figsize = figsize

    def scatter(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "",
        output: Optional[str] = None,
    ):
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.scatter(df[x], df[y])

        ax.set_title(title)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.grid(True)

        fig.tight_layout()

        if output:
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output, dpi=300)

        return fig

    def histogram(
        self,
        df: pd.DataFrame,
        column: str,
        bins: int = 20,
        title: str = "",
        output: Optional[str] = None,
    ):
        fig, ax = plt.subplots(figsize=self.figsize)

        ax.hist(df[column], bins=bins)

        ax.set_title(title)
        ax.set_xlabel(column)
        ax.set_ylabel("Frequency")

        fig.tight_layout()

        if output:
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output, dpi=300)

        return fig


plots = PlotGenerator()