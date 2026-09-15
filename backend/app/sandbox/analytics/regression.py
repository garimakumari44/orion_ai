"""
Regression utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso,
)

from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error,
)


@dataclass
class RegressionResult:
    r2: float
    mae: float
    mse: float
    coefficients: list[float]
    intercept: float
    model: Any


class RegressionAnalyzer:
    """Regression helper methods."""

    def linear(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> RegressionResult:

        model = LinearRegression()

        model.fit(X, y)

        pred = model.predict(X)

        return RegressionResult(
            r2=r2_score(y, pred),
            mae=mean_absolute_error(y, pred),
            mse=mean_squared_error(y, pred),
            coefficients=model.coef_.tolist(),
            intercept=float(model.intercept_),
            model=model,
        )

    def ridge(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        alpha: float = 1.0,
    ) -> RegressionResult:

        model = Ridge(alpha=alpha)

        model.fit(X, y)

        pred = model.predict(X)

        return RegressionResult(
            r2=r2_score(y, pred),
            mae=mean_absolute_error(y, pred),
            mse=mean_squared_error(y, pred),
            coefficients=model.coef_.tolist(),
            intercept=float(model.intercept_),
            model=model,
        )

    def lasso(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        alpha: float = 1.0,
    ) -> RegressionResult:

        model = Lasso(alpha=alpha)

        model.fit(X, y)

        pred = model.predict(X)

        return RegressionResult(
            r2=r2_score(y, pred),
            mae=mean_absolute_error(y, pred),
            mse=mean_squared_error(y, pred),
            coefficients=model.coef_.tolist(),
            intercept=float(model.intercept_),
            model=model,
        )