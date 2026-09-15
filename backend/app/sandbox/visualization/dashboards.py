"""
dashboards.py
-------------

Utilities for building dashboard-style visualizations.

Features
--------
- Multiple charts in one figure
- Automatic subplot layout
- Save dashboard as image
- Reusable API

Example
-------
dashboard = Dashboard(rows=2, cols=2)
dashboard.add_line(...)
dashboard.add_bar(...)
dashboard.save("dashboard.png")
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


class Dashboard:
    """Simple dashboard builder using matplotlib subplots."""

    def __init__(
        self,
        rows: int = 2,
        cols: int = 2,
        figsize=(14, 8),
        title: str = "Analytics Dashboard",
    ):
        self.rows = rows
        self.cols = cols

        self.figure, self.axes = plt.subplots(rows, cols, figsize=figsize)

        # Flatten axes for easy indexing
        if hasattr(self.axes, "flatten"):
            self.axes = self.axes.flatten()
        else:
            self.axes = [self.axes]

        self.current = 0
        self.figure.suptitle(title, fontsize=18)

    def _next_axis(self):
        if self.current >= len(self.axes):
            raise RuntimeError("Dashboard is full.")
        ax = self.axes[self.current]
        self.current += 1
        return ax

    def add_line(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "",
    ):
        ax = self._next_axis()

        ax.plot(df[x], df[y], linewidth=2)
        ax.set_title(title)
        ax.grid(True)

    def add_bar(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "",
    ):
        ax = self._next_axis()

        ax.bar(df[x], df[y])
        ax.set_title(title)

    def add_scatter(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "",
    ):
        ax = self._next_axis()

        ax.scatter(df[x], df[y])
        ax.set_title(title)
        ax.grid(True)

    def add_histogram(
        self,
        df: pd.DataFrame,
        column: str,
        bins: int = 20,
        title: str = "",
    ):
        ax = self._next_axis()

        ax.hist(df[column], bins=bins)
        ax.set_title(title)

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        self.figure.tight_layout()
        self.figure.savefig(path, dpi=300)

    def show(self):
        self.figure.tight_layout()
        plt.show()