"""
Clustering algorithms.

Supported:
- K-Means
- DBSCAN
- Agglomerative Clustering
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import pandas as pd
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score


@dataclass
class ClusteringResult:
    labels: list[int]
    n_clusters: int
    silhouette_score: Optional[float]
    model: Any


class ClusterAnalyzer:
    """Utility class for clustering datasets."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def kmeans(
        self,
        data: pd.DataFrame,
        n_clusters: int = 3,
    ) -> ClusteringResult:

        model = KMeans(
            n_clusters=n_clusters,
            random_state=self.random_state,
            n_init="auto",
        )

        labels = model.fit_predict(data)

        score = (
            silhouette_score(data, labels)
            if len(set(labels)) > 1
            else None
        )

        return ClusteringResult(
            labels=labels.tolist(),
            n_clusters=n_clusters,
            silhouette_score=score,
            model=model,
        )

    def dbscan(
        self,
        data: pd.DataFrame,
        eps: float = 0.5,
        min_samples: int = 5,
    ) -> ClusteringResult:

        model = DBSCAN(
            eps=eps,
            min_samples=min_samples,
        )

        labels = model.fit_predict(data)

        clusters = len(set(labels)) - (1 if -1 in labels else 0)

        score = (
            silhouette_score(data, labels)
            if clusters > 1
            else None
        )

        return ClusteringResult(
            labels=labels.tolist(),
            n_clusters=clusters,
            silhouette_score=score,
            model=model,
        )

    def hierarchical(
        self,
        data: pd.DataFrame,
        n_clusters: int = 3,
    ) -> ClusteringResult:

        model = AgglomerativeClustering(
            n_clusters=n_clusters
        )

        labels = model.fit_predict(data)

        score = (
            silhouette_score(data, labels)
            if len(set(labels)) > 1
            else None
        )

        return ClusteringResult(
            labels=labels.tolist(),
            n_clusters=n_clusters,
            silhouette_score=score,
            model=model,
        )