"""
Analytics Package

Provides statistical analysis, forecasting, anomaly detection,
clustering, regression, KPI computation, and summarization
utilities for the AI Analytics Platform.

Example:
    from analytics import (
        StatisticsAnalyzer,
        MetricsCalculator,
        ForecastEngine,
        AnomalyDetector,
        ClusterAnalyzer,
        RegressionAnalyzer,
        DataSummarizer,
    )
"""

from .statistics import StatisticsAnalyzer
from .metrics import MetricsCalculator
from .forecasting import ForecastEngine
from .anomaly import AnomalyDetector
from .clustering import ClusterAnalyzer
from .regression import RegressionAnalyzer
from .summarization import DataSummarizer

__all__ = [
    "StatisticsAnalyzer",
    "MetricsCalculator",
    "ForecastEngine",
    "AnomalyDetector",
    "ClusterAnalyzer",
    "RegressionAnalyzer",
    "DataSummarizer",
]

__version__ = "1.0.0"
__author__ = "Orion AI"