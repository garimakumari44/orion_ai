"""
Score calibration utilities.

Normalizes retrieval scores from
multiple retrieval systems.
"""

from __future__ import annotations

from typing import List

import numpy as np


class ScoreCalibrator:
    """
    Normalize scores into [0,1].

    Supports:
    - Min-Max
    - Softmax
    - Z-score
    """

    @staticmethod
    def min_max(
        scores: List[float],
    ) -> List[float]:

        if not scores:
            return []

        low = min(scores)
        high = max(scores)

        if high == low:
            return [1.0] * len(scores)

        return [
            (x - low) / (high - low)
            for x in scores
        ]

    @staticmethod
    def softmax(
        scores: List[float],
    ) -> List[float]:

        if not scores:
            return []

        values = np.array(scores)

        exp = np.exp(values - np.max(values))

        probs = exp / exp.sum()

        return probs.tolist()

    @staticmethod
    def z_score(
        scores: List[float],
    ) -> List[float]:

        if not scores:
            return []

        values = np.array(scores)

        mean = values.mean()
        std = values.std()

        if std == 0:
            return [0.0] * len(scores)

        return (
            (values - mean) / std
        ).tolist()

    def calibrate_chunks(
        self,
        chunks,
        method: str = "min_max",
    ):

        scores = [
            getattr(c, "score", 0.0)
            for c in chunks
        ]

        if method == "min_max":
            normalized = self.min_max(scores)

        elif method == "softmax":
            normalized = self.softmax(scores)

        elif method == "z_score":
            normalized = self.z_score(scores)

        else:
            raise ValueError(
                f"Unknown calibration method: {method}"
            )

        for chunk, score in zip(
            chunks,
            normalized,
        ):
            chunk.score = score

        return chunks