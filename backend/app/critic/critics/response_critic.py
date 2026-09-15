"""
Response Critic.

Aggregates evaluator scores and critic reports into a
single response quality assessment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from statistics import mean
from typing import Any, Dict, List, Optional


class ResponseQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    FAILED = "failed"


@dataclass
class ResponseCritique:
    """
    Final critique of an AI response.
    """

    quality: ResponseQuality
    overall_score: float

    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    evaluator_scores: Dict[str, float] = field(default_factory=dict)

    warnings: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


class ResponseCritic:
    """
    Produces an overall assessment from multiple evaluator
    scores and critic outputs.
    """

    def __init__(
        self,
        warning_threshold: float = 0.70,
        failure_threshold: float = 0.50,
    ):
        self.warning_threshold = warning_threshold
        self.failure_threshold = failure_threshold

    def critique(
        self,
        evaluator_scores: Dict[str, float],
        critic_reports: Optional[List[Any]] = None,
    ) -> ResponseCritique:

        critic_reports = critic_reports or []

        overall_score = (
            mean(evaluator_scores.values())
            if evaluator_scores
            else 0.0
        )

        warnings: List[str] = []
        issues: List[str] = []
        strengths: List[str] = []
        weaknesses: List[str] = []
        recommendations: List[str] = []

        # -----------------------------
        # Analyze evaluator scores
        # -----------------------------

        for metric, score in evaluator_scores.items():

            if score >= 0.90:
                strengths.append(
                    f"{metric.capitalize()} is excellent."
                )

            elif score >= self.warning_threshold:
                strengths.append(
                    f"{metric.capitalize()} is acceptable."
                )

            elif score >= self.failure_threshold:
                warnings.append(
                    f"{metric.capitalize()} needs improvement."
                )

                weaknesses.append(metric)

            else:
                issues.append(
                    f"{metric.capitalize()} failed quality threshold."
                )

                weaknesses.append(metric)

        # -----------------------------
        # Merge recommendations
        # -----------------------------

        for report in critic_reports:

            if hasattr(report, "recommendations"):
                recommendations.extend(report.recommendations)

            if hasattr(report, "warnings"):
                warnings.extend(report.warnings)

            if hasattr(report, "issues"):
                issues.extend(report.issues)

        # Remove duplicates

        strengths = sorted(set(strengths))
        weaknesses = sorted(set(weaknesses))
        warnings = sorted(set(warnings))
        issues = sorted(set(issues))
        recommendations = sorted(set(recommendations))

        # -----------------------------
        # Overall quality
        # -----------------------------

        if overall_score >= 0.90:
            quality = ResponseQuality.EXCELLENT

        elif overall_score >= 0.80:
            quality = ResponseQuality.GOOD

        elif overall_score >= 0.65:
            quality = ResponseQuality.FAIR

        elif overall_score >= 0.50:
            quality = ResponseQuality.POOR

        else:
            quality = ResponseQuality.FAILED

        # -----------------------------
        # Automatic recommendations
        # -----------------------------

        if "hallucination" in weaknesses:
            recommendations.append(
                "Reduce unsupported factual claims."
            )

        if "citation" in weaknesses:
            recommendations.append(
                "Add reliable citations."
            )

        if "reasoning" in weaknesses:
            recommendations.append(
                "Improve reasoning clarity."
            )

        if "completeness" in weaknesses:
            recommendations.append(
                "Provide a more complete answer."
            )

        if "toxicity" in weaknesses:
            recommendations.append(
                "Remove unsafe or toxic language."
            )

        return ResponseCritique(
            quality=quality,
            overall_score=round(overall_score, 3),
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=sorted(set(recommendations)),
            evaluator_scores=evaluator_scores,
            warnings=warnings,
            issues=issues,
            metadata={
                "num_metrics": len(evaluator_scores),
                "num_critic_reports": len(critic_reports),
            },
        )