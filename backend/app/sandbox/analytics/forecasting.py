"""
Forecasting utilities.

Provides simple forecasting models including:

- Moving Average
- Exponential Smoothing
- Linear Trend Forecast
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


class Forecasting:
    """Simple forecasting algorithms."""

    @staticmethod
    def moving_average(
        series: pd.Series,
        window: int = 5,
    ) -> pd.Series:
        """
        Moving average smoothing.
        """
        return series.rolling(window=window).mean()

    @staticmethod
    def exponential_smoothing(
        series: pd.Series,
        alpha: float = 0.3,
    ) -> pd.Series:
        """
        Exponential weighted moving average.
        """
        return series.ewm(alpha=alpha, adjust=False).mean()

    @staticmethod
    def linear_forecast(
        series: pd.Series,
        periods: int = 5,
    ) -> pd.Series:
        """
        Forecast future values using a simple linear trend.
        """

        values = series.dropna().to_numpy()

        if len(values) < 2:
            raise ValueError("At least two observations required.")

        x = np.arange(len(values))

        slope, intercept = np.polyfit(x, values, 1)

        future_x = np.arange(len(values), len(values) + periods)

        forecast = intercept + slope * future_x

        return pd.Series(
            forecast,
            index=range(len(values), len(values) + periods),
            name="forecast",
        )

    @staticmethod
    def forecast_mean(
        series: pd.Series,
        periods: int = 5,
    ) -> pd.Series:
        """
        Naive forecast using historical mean.
        """

        mean = series.mean()

        return pd.Series(
            [mean] * periods,
            name="forecast",
        )

    @staticmethod
    def forecast_last(
        series: pd.Series,
        periods: int = 5,
    ) -> pd.Series:
        """
        Forecast using the last observed value.
        """

        value = series.iloc[-1]

        return pd.Series(
            [value] * periods,
            name="forecast",
        )

    @staticmethod
    def forecast_growth(
        current: float,
        growth_rate: float,
        periods: int,
    ) -> pd.Series:
        """
        Compound growth forecast.

        growth_rate = 0.10 means 10%
        """

        values = []

        value = current

        for _ in range(periods):
            value *= (1 + growth_rate)
            values.append(value)

        return pd.Series(values)