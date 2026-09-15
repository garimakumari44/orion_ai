"""
Business KPI and metric computation utilities.
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


class Metrics:
    """Collection of common business metrics."""

    @staticmethod
    def growth_rate(previous: float, current: float) -> float:
        """
        Percentage growth.

        Returns:
            %
        """
        if previous == 0:
            return np.nan

        return ((current - previous) / previous) * 100

    @staticmethod
    def conversion_rate(conversions: float, visitors: float) -> float:
        """Conversion rate."""
        if visitors == 0:
            return np.nan

        return conversions / visitors

    @staticmethod
    def retention_rate(active_users: float, total_users: float) -> float:
        """Retention rate."""
        if total_users == 0:
            return np.nan

        return active_users / total_users

    @staticmethod
    def churn_rate(churned: float, customers: float) -> float:
        """Customer churn."""
        if customers == 0:
            return np.nan

        return churned / customers

    @staticmethod
    def average_order_value(revenue: float, orders: float) -> float:
        """Average order value."""
        if orders == 0:
            return np.nan

        return revenue / orders

    @staticmethod
    def customer_lifetime_value(
        avg_purchase: float,
        purchase_frequency: float,
        lifespan: float,
    ) -> float:
        """
        Customer lifetime value.
        """

        return avg_purchase * purchase_frequency * lifespan

    @staticmethod
    def roi(gain: float, cost: float) -> float:
        """
        Return on Investment.
        """

        if cost == 0:
            return np.nan

        return ((gain - cost) / cost) * 100

    @staticmethod
    def gross_margin(revenue: float, cost: float) -> float:
        """
        Gross margin.
        """

        if revenue == 0:
            return np.nan

        return (revenue - cost) / revenue

    @staticmethod
    def summarize_dataframe(df: pd.DataFrame) -> Dict[str, float]:
        """
        Simple numeric KPI summary.
        """

        numeric = df.select_dtypes(include=np.number)

        return {
            "rows": float(len(df)),
            "columns": float(len(df.columns)),
            "missing_values": float(df.isna().sum().sum()),
            "numeric_columns": float(len(numeric.columns)),
            "total_sum": float(numeric.sum().sum()),
            "overall_mean": float(numeric.mean().mean()),
        }