"""
Anomaly detection utilities.

Supports:

- Z-score detection
- IQR detection
- Rolling statistics
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class AnomalyDetection:
    """Detect anomalies in numeric data."""

    @staticmethod
    def z_score(
        series: pd.Series,
        threshold: float = 3.0,
    ) -> pd.Series:
        """
        Boolean mask using Z-score.
        """

        std = series.std()

        if std == 0:
            return pd.Series(False, index=series.index)

        z = (series - series.mean()) / std

        return z.abs() > threshold

    @staticmethod
    def iqr(
        series: pd.Series,
        multiplier: float = 1.5,
    ) -> pd.Series:
        """
        Detect anomalies using IQR.
        """

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr

        return (series < lower) | (series > upper)

    @staticmethod
    def rolling_anomaly(
        series: pd.Series,
        window: int = 10,
        threshold: float = 2.5,
    ) -> pd.Series:
        """
        Rolling window anomaly detection.
        """

        rolling_mean = series.rolling(window).mean()
        rolling_std = series.rolling(window).std()

        deviation = (series - rolling_mean).abs()

        return deviation > threshold * rolling_std

    @staticmethod
    def anomaly_scores(series: pd.Series) -> pd.Series:
        """
        Continuous anomaly score using Z-score.
        """

        std = series.std()

        if std == 0:
            return pd.Series(
                np.zeros(len(series)),
                index=series.index,
            )

        return ((series - series.mean()) / std).abs()

    @staticmethod
    def remove_outliers(
        series: pd.Series,
        method: str = "iqr",
    ) -> pd.Series:
        """
        Remove detected outliers.

        Methods:
            - iqr
            - zscore
        """

        if method == "iqr":
            mask = AnomalyDetection.iqr(series)
        elif method == "zscore":
            mask = AnomalyDetection.z_score(series)
        else:
            raise ValueError("Unknown method.")

        return series[~mask]