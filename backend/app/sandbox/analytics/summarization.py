"""
Automatic dataset summarization.
"""

from __future__ import annotations

from typing import Dict, Any

import pandas as pd


class DataSummarizer:
    """Generate high-level summaries of datasets."""

    def summarize(self, df: pd.DataFrame) -> Dict[str, Any]:

        numeric = df.select_dtypes(include="number")

        return {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_mb": round(
                df.memory_usage(deep=True).sum() / 1024**2,
                2,
            ),
            "missing_values": df.isna().sum().to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
            "dtypes": {
                k: str(v)
                for k, v in df.dtypes.items()
            },
            "numeric_summary": numeric.describe().to_dict()
            if not numeric.empty
            else {},
        }

    def categorical_summary(
        self,
        df: pd.DataFrame,
    ) -> Dict[str, Any]:

        result = {}

        for column in df.select_dtypes(
            include=["object", "category"]
        ):

            result[column] = {
                "unique": int(df[column].nunique()),
                "top_values": (
                    df[column]
                    .value_counts()
                    .head(10)
                    .to_dict()
                ),
            }

        return result

    def correlation_summary(
        self,
        df: pd.DataFrame,
    ) -> Dict[str, Any]:

        numeric = df.select_dtypes(include="number")

        if numeric.empty:
            return {}

        return numeric.corr().to_dict()