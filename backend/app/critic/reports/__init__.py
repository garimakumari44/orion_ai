"""
Reports Package

Provides reporting utilities for the AI evaluation framework.

Modules:
    - summary:
        Human-readable evaluation reports

    - metrics:
        Evaluation metrics calculation

    - diagnostics:
        Detailed failure analysis and recommendations

    - visualization:
        Dashboard-ready visualization data
"""


from .summary import ReportGenerator
from .metrics import MetricsCalculator
from .diagnostics import DiagnosticAnalyzer
from .visualization import VisualizationBuilder



__all__ = [

    # Summary reports
    "ReportGenerator",

    # Metrics
    "MetricsCalculator",

    # Diagnostics
    "DiagnosticAnalyzer",

    # Visualization
    "VisualizationBuilder",

]