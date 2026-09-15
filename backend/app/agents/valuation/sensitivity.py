"""
app/agents/valuation/sensitivity.py

Valuation Sensitivity Analysis
==============================

Provides sensitivity analysis for valuation models.

The sensitivity layer is intentionally defensive because valuation
calculations can produce NaN or infinity when inputs are missing,
invalid, extreme, or involve division by zero.

Design principles
-----------------

1. Never expose NaN or infinity in public results.
2. Invalid calculations return None instead of invalid floats.
3. Valid zero values are preserved.
4. Inputs are normalized before calculations.
5. Sensitivity calculations remain deterministic.
6. The output is safe for JSON serialization.
7. The module does not hide genuine calculation failures behind
   fabricated financial values.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Optional


class SensitivityAnalysis:
    """
    Performs valuation sensitivity analysis.

    The class supports sensitivity analysis across two dimensions,
    typically WACC and terminal growth rate.

    Example
    -------

    analyzer = SensitivityAnalysis()

    result = analyzer.calculate(
        base_value=100.0,
        discount_rates=[0.08, 0.09, 0.10],
        terminal_growth_rates=[0.02, 0.03, 0.04],
    )
    """

    def __init__(self) -> None:
        """Initialize the sensitivity analyzer."""
        pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate(
        self,
        base_value: Any,
        discount_rates: Iterable[Any],
        terminal_growth_rates: Iterable[Any],
    ) -> Dict[str, Any]:
        """
        Calculate a valuation sensitivity matrix.

        Parameters
        ----------
        base_value:
            Base valuation.

        discount_rates:
            WACC / discount-rate scenarios.

        terminal_growth_rates:
            Terminal-growth-rate scenarios.

        Returns
        -------
        dict
            JSON-safe sensitivity result.

        Notes
        -----
        This method deliberately returns ``None`` for invalid/non-finite
        cells rather than allowing NaN or infinity into the response.
        """

        base = self._safe_float(base_value)

        rates = self._sanitize_sequence(discount_rates)
        growth_rates = self._sanitize_sequence(terminal_growth_rates)

        matrix: List[List[Optional[float]]] = []

        for discount_rate in rates:
            row: List[Optional[float]] = []

            for growth_rate in growth_rates:
                value = self._calculate_sensitivity_value(
                    base_value=base,
                    discount_rate=discount_rate,
                    terminal_growth_rate=growth_rate,
                )

                row.append(value)

            matrix.append(row)

        return {
            "base_value": base,
            "discount_rates": rates,
            "terminal_growth_rates": growth_rates,
            "values": matrix,
        }

    def calculate_matrix(
        self,
        base_value: Any,
        discount_rates: Iterable[Any],
        terminal_growth_rates: Iterable[Any],
    ) -> List[List[Optional[float]]]:
        """
        Calculate only the sensitivity matrix.

        This is useful for callers that already maintain their own
        response structure.
        """

        base = self._safe_float(base_value)

        rates = self._sanitize_sequence(discount_rates)
        growth_rates = self._sanitize_sequence(terminal_growth_rates)

        return [
            [
                self._calculate_sensitivity_value(
                    base_value=base,
                    discount_rate=discount_rate,
                    terminal_growth_rate=growth_rate,
                )
                for growth_rate in growth_rates
            ]
            for discount_rate in rates
        ]

    # ------------------------------------------------------------------
    # Core sensitivity calculation
    # ------------------------------------------------------------------

    def _calculate_sensitivity_value(
        self,
        base_value: Optional[float],
        discount_rate: Optional[float],
        terminal_growth_rate: Optional[float],
    ) -> Optional[float]:
        """
        Calculate one sensitivity-cell value.

        Uses the standard Gordon-growth adjustment:

            Value = BaseValue * (1 + g) / (r - g)

        where:

            r = discount rate
            g = terminal growth rate

        The calculation is rejected when the denominator is zero,
        negative, or otherwise non-finite.

        A negative ``r - g`` would imply an invalid terminal-value
        setup for this sensitivity model and is therefore represented
        as ``None``.
        """

        if base_value is None:
            return None

        if discount_rate is None:
            return None

        if terminal_growth_rate is None:
            return None

        if not self._is_finite(base_value):
            return None

        if not self._is_finite(discount_rate):
            return None

        if not self._is_finite(terminal_growth_rate):
            return None

        denominator = discount_rate - terminal_growth_rate

        if not self._is_finite(denominator):
            return None

        # Prevent division by zero and numerically unstable values.
        if denominator <= 0.0:
            return None

        numerator = base_value * (1.0 + terminal_growth_rate)

        if not self._is_finite(numerator):
            return None

        try:
            value = numerator / denominator
        except (ArithmeticError, OverflowError, ZeroDivisionError):
            return None

        return self._safe_float(value)

    # ------------------------------------------------------------------
    # Optional percentage-change sensitivity
    # ------------------------------------------------------------------

    def calculate_percentage_change(
        self,
        base_value: Any,
        sensitivity_value: Any,
    ) -> Optional[float]:
        """
        Calculate percentage change from the base valuation.

            ((sensitivity - base) / abs(base)) * 100

        Returns ``None`` when either value is invalid or when the
        base value is zero.
        """

        base = self._safe_float(base_value)
        value = self._safe_float(sensitivity_value)

        if base is None or value is None:
            return None

        if base == 0.0:
            return None

        try:
            result = ((value - base) / abs(base)) * 100.0
        except (ArithmeticError, OverflowError, ZeroDivisionError):
            return None

        return self._safe_float(result)

    # ------------------------------------------------------------------
    # Scenario helpers
    # ------------------------------------------------------------------

    def build_scenarios(
        self,
        base_discount_rate: Any,
        base_terminal_growth_rate: Any,
        discount_rate_steps: Iterable[Any] = (-0.02, -0.01, 0.0, 0.01, 0.02),
        growth_rate_steps: Iterable[Any] = (-0.01, 0.0, 0.01),
    ) -> Dict[str, List[float]]:
        """
        Build discount-rate and terminal-growth-rate scenarios.

        Invalid base values produce empty scenario lists instead of
        propagating invalid numeric values.
        """

        base_discount = self._safe_float(base_discount_rate)
        base_growth = self._safe_float(base_terminal_growth_rate)

        if base_discount is None or base_growth is None:
            return {
                "discount_rates": [],
                "terminal_growth_rates": [],
            }

        discount_rates: List[float] = []
        growth_rates: List[float] = []

        for step in discount_rate_steps:
            step_value = self._safe_float(step)

            if step_value is None:
                continue

            rate = self._safe_float(base_discount + step_value)

            if rate is not None:
                discount_rates.append(rate)

        for step in growth_rate_steps:
            step_value = self._safe_float(step)

            if step_value is None:
                continue

            growth = self._safe_float(base_growth + step_value)

            if growth is not None:
                growth_rates.append(growth)

        return {
            "discount_rates": discount_rates,
            "terminal_growth_rates": growth_rates,
        }

    # ------------------------------------------------------------------
    # Serialization safety
    # ------------------------------------------------------------------

    def sanitize_result(self, value: Any) -> Any:
        """
        Recursively sanitize a result so it is safe for JSON encoding.

        Non-finite floats become ``None``.

        This method also handles nested dictionaries, lists, tuples,
        and sets.
        """

        if isinstance(value, float):
            return value if math.isfinite(value) else None

        if isinstance(value, int):
            return value

        if isinstance(value, dict):
            return {
                key: self.sanitize_result(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [self.sanitize_result(item) for item in value]

        if isinstance(value, tuple):
            return [
                self.sanitize_result(item)
                for item in value
            ]

        if isinstance(value, set):
            return [
                self.sanitize_result(item)
                for item in value
            ]

        return value

    # ------------------------------------------------------------------
    # Numeric helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_finite(value: Any) -> bool:
        """
        Return True only for finite numeric values.
        """

        if isinstance(value, bool):
            return False

        if not isinstance(value, (int, float)):
            return False

        try:
            return math.isfinite(float(value))
        except (TypeError, ValueError, OverflowError):
            return False

    @classmethod
    def _safe_float(cls, value: Any) -> Optional[float]:
        """
        Convert a value to a finite float.

        Returns ``None`` for:

        - None
        - NaN
        - +inf
        - -inf
        - invalid strings
        - unsupported values
        - booleans
        """

        if value is None:
            return None

        if isinstance(value, bool):
            return None

        try:
            converted = float(value)
        except (TypeError, ValueError, OverflowError):
            return None

        if not math.isfinite(converted):
            return None

        return converted

    @classmethod
    def _sanitize_sequence(
        cls,
        values: Iterable[Any],
    ) -> List[Optional[float]]:
        """
        Convert a sequence of values into finite floats.

        Invalid entries are retained as ``None`` so the matrix preserves
        the original scenario positions.
        """

        if values is None:
            return []

        try:
            iterator = iter(values)
        except TypeError:
            return []

        result: List[Optional[float]] = []

        for value in iterator:
            result.append(cls._safe_float(value))

        return result


# ----------------------------------------------------------------------
# Backward-compatible aliases
# ----------------------------------------------------------------------

SensitivityAnalyzer = SensitivityAnalysis


__all__ = [
    "SensitivityAnalysis",
    "SensitivityAnalyzer",
]