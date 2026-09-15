"""
Statistical analysis utilities.

Provides descriptive statistics, correlation analysis,
distribution summaries, and hypothesis testing helpers.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd


class Statistics:
    """Statistical analysis helper."""

    @staticmethod
    def describe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Return descriptive statistics.

        Parameters
        ----------
        df : DataFrame

        Returns
        -------
        DataFrame
        """
        return df.describe(include="all")

    @staticmethod
    def summary(series: pd.Series) -> Dict[str, float]:
        """
        Summary statistics for one column.
        """

        s = series.dropna()

        return {
            "count": float(s.count()),
            "mean": float(s.mean()),
            "median": float(s.median()),
            "std": float(s.std()),
            "variance": float(s.var()),
            "min": float(s.min()),
            "max": float(s.max()),
            "q25": float(s.quantile(0.25)),
            "q75": float(s.quantile(0.75)),
            "skew": float(s.skew()),
            "kurtosis": float(s.kurt()),
        }

    @staticmethod
    def correlation(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
        """
        Correlation matrix.

        Methods:
            - pearson
            - spearman
            - kendall
        """
        return df.corr(method=method, numeric_only=True)

    @staticmethod
    def covariance(df: pd.DataFrame) -> pd.DataFrame:
        """Covariance matrix."""
        return df.cov(numeric_only=True)

    @staticmethod
    def missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """
        Missing value report.
        """

        return pd.DataFrame(
            {
                "missing": df.isna().sum(),
                "percentage": df.isna().mean() * 100,
            }
        )

    @staticmethod
    def percentile(series: pd.Series, q: float) -> float:
        """Compute percentile."""
        return float(np.percentile(series.dropna(), q))

    @staticmethod
    def outlier_bounds(series: pd.Series):
        """
        IQR-based outlier limits.
        """

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        return lower, upper

    @staticmethod
    def detect_outliers(series: pd.Series) -> pd.Series:
        """
        Boolean mask of outliers.
        """

        lower, upper = Statistics.outlier_bounds(series)

        return (series < lower) | (series > upper)

    @staticmethod
    def numeric_columns(df: pd.DataFrame) -> List[str]:
        """Return numeric columns."""
        return list(df.select_dtypes(include=np.number).columns)