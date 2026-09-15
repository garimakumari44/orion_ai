"""
app/agents/valuation/dcf.py

Discounted Cash Flow Valuation Model.

Responsibilities
----------------
- Project future free cash flows.
- Calculate present value of projected cash flows.
- Calculate terminal value.
- Calculate enterprise value.
- Calculate equity value.
- Calculate fair value per share.
- Validate all numeric inputs.
- Prevent NaN / +inf / -inf from entering DCFResult.

IMPORTANT
---------
DCF calculations must never silently produce non-finite values.

Invalid inputs such as:

    NaN
    +inf
    -inf

or mathematically invalid assumptions such as:

    discount_rate <= terminal_growth

must raise a clear ValueError before a non-JSON-safe value can
propagate through the financial analysis pipeline.
"""

from __future__ import annotations

import math
from typing import List

from .models import DCFResult


class DCFModel:
    """
    Discounted Cash Flow valuation model.

    Calculates intrinsic company value based on projected future
    free cash flows.

    The model validates all numerical assumptions and intermediate
    results so that NaN or infinite values cannot propagate into
    DCFResult.
    """

    # =========================================================
    # Initialization
    # =========================================================

    def __init__(
        self,
        growth_rate: float,
        discount_rate: float,
        terminal_growth: float = 0.03,
    ) -> None:
        """
        Initialize the DCF model.

        Parameters
        ----------
        growth_rate:
            Expected annual FCF growth rate.

        discount_rate:
            Discount rate / WACC.

        terminal_growth:
            Long-term perpetual growth rate.

        Raises
        ------
        ValueError
            If any supplied value is NaN or infinite.

        ValueError
            If discount_rate is not greater than terminal_growth.
        """

        self.growth_rate = self._validate_finite(
            growth_rate,
            "growth_rate",
        )

        self.discount_rate = self._validate_finite(
            discount_rate,
            "discount_rate",
        )

        self.terminal_growth = self._validate_finite(
            terminal_growth,
            "terminal_growth",
        )

        # -----------------------------------------------------
        # Gordon Growth Model requirement
        #
        # Terminal Value:
        #
        #     FCF * (1 + g)
        #     ----------------
        #          r - g
        #
        # Therefore:
        #
        #     r > g
        #
        # must always hold.
        # -----------------------------------------------------

        if self.discount_rate <= self.terminal_growth:
            raise ValueError(
                "discount_rate must be greater than "
                "terminal_growth. "
                f"Got discount_rate={self.discount_rate!r}, "
                f"terminal_growth={self.terminal_growth!r}."
            )

    # =========================================================
    # Cash Flow Projection
    # =========================================================

    def project_cashflows(
        self,
        initial_fcf: float,
        years: int = 5,
    ) -> List[float]:
        """
        Project future free cash flows.

        Parameters
        ----------
        initial_fcf:
            Starting free cash flow.

        years:
            Number of projection years.

        Returns
        -------
        list[float]
            Projected free cash flows.

        Raises
        ------
        ValueError
            If initial_fcf is non-finite.

        ValueError
            If years is invalid.

        ValueError
            If a projected cash flow becomes non-finite.
        """

        initial_fcf = self._validate_finite(
            initial_fcf,
            "initial_fcf",
        )

        # -----------------------------------------------------
        # Validate projection horizon
        # -----------------------------------------------------

        if not isinstance(years, int):
            raise TypeError(
                "years must be an integer."
            )

        if isinstance(years, bool):
            raise TypeError(
                "years must be an integer, not bool."
            )

        if years <= 0:
            raise ValueError(
                "years must be greater than zero."
            )

        # -----------------------------------------------------
        # Project cash flows
        # -----------------------------------------------------

        cashflows: List[float] = []

        current = initial_fcf

        for year in range(1, years + 1):
            current *= 1.0 + self.growth_rate

            current = self._validate_finite(
                current,
                f"projected_cashflow_year_{year}",
            )

            cashflows.append(current)

        if not cashflows:
            raise ValueError(
                "DCF projection produced no cash flows."
            )

        return cashflows

    # =========================================================
    # Present Value
    # =========================================================

    def calculate_present_value(
        self,
        cashflows: List[float],
    ) -> float:
        """
        Calculate the present value of projected cash flows.

        Each cash flow is discounted using:

            PV = FCF / (1 + discount_rate)^year

        Raises
        ------
        ValueError
            If cashflows contains non-finite values.

        ValueError
            If the discount factor becomes invalid.

        ValueError
            If the final present value is non-finite.
        """

        if not isinstance(cashflows, (list, tuple)):
            raise TypeError(
                "cashflows must be a list or tuple of numeric values."
            )

        if not cashflows:
            raise ValueError(
                "cashflows must contain at least one value."
            )

        value = 0.0

        discount_base = 1.0 + self.discount_rate

        # -----------------------------------------------------
        # Validate discount base
        # -----------------------------------------------------

        discount_base = self._validate_finite(
            discount_base,
            "discount_base",
        )

        if discount_base <= 0.0:
            raise ValueError(
                "1 + discount_rate must be greater than zero. "
                f"Got discount_rate={self.discount_rate!r}."
            )

        # -----------------------------------------------------
        # Discount each cash flow
        # -----------------------------------------------------

        for year, cashflow in enumerate(
            cashflows,
            start=1,
        ):
            cashflow = self._validate_finite(
                cashflow,
                f"cashflow_year_{year}",
            )

            try:
                discount_factor = discount_base ** year
            except (OverflowError, ValueError) as exc:
                raise ValueError(
                    "DCF discount factor became invalid at "
                    f"year {year}."
                ) from exc

            discount_factor = self._validate_finite(
                discount_factor,
                f"discount_factor_year_{year}",
            )

            if discount_factor == 0.0:
                raise ValueError(
                    "DCF discount factor became zero at "
                    f"year {year}."
                )

            discounted = cashflow / discount_factor

            discounted = self._validate_finite(
                discounted,
                f"discounted_cashflow_year_{year}",
            )

            value += discounted

            value = self._validate_finite(
                value,
                f"present_value_after_year_{year}",
            )

        return value

    # =========================================================
    # Terminal Value
    # =========================================================

    def calculate_terminal_value(
        self,
        final_cashflow: float,
    ) -> float:
        """
        Calculate terminal value using the Gordon Growth Model.

        Formula:

            Terminal Value =
                final FCF * (1 + terminal growth)
                --------------------------------
                discount rate - terminal growth

        Raises
        ------
        ValueError
            If final_cashflow is non-finite.

        ValueError
            If discount_rate <= terminal_growth.

        ValueError
            If the calculated terminal value is non-finite.
        """

        final_cashflow = self._validate_finite(
            final_cashflow,
            "final_cashflow",
        )

        denominator = (
            self.discount_rate
            - self.terminal_growth
        )

        denominator = self._validate_finite(
            denominator,
            "terminal_value_denominator",
        )

        if denominator <= 0.0:
            raise ValueError(
                "DCF terminal value is undefined because "
                "discount_rate must be greater than "
                "terminal_growth. "
                f"discount_rate={self.discount_rate!r}, "
                f"terminal_growth={self.terminal_growth!r}."
            )

        numerator = (
            final_cashflow
            * (1.0 + self.terminal_growth)
        )

        numerator = self._validate_finite(
            numerator,
            "terminal_value_numerator",
        )

        terminal_value = numerator / denominator

        return self._validate_finite(
            terminal_value,
            "terminal_value",
        )

    # =========================================================
    # Full DCF Calculation
    # =========================================================

    def calculate(
        self,
        free_cash_flow: float,
        shares_outstanding: float,
    ) -> DCFResult:
        """
        Perform the complete DCF valuation.

        Calculation flow:

            FCF
             |
             v
        Project FCFs
             |
             v
        PV of FCFs
             |
             +--------+
             |        |
             v        v
          Terminal   Discount
           Value     Terminal
             |        Value
             +--------+
                  |
                  v
          Enterprise Value
                  |
                  v
             Equity Value
                  |
                  v
          Fair Value / Share

        Raises
        ------
        ValueError
            If any input or intermediate calculation is invalid.

        The method guarantees that all numeric fields placed into
        DCFResult are finite.
        """

        # -----------------------------------------------------
        # Validate inputs
        # -----------------------------------------------------

        free_cash_flow = self._validate_finite(
            free_cash_flow,
            "free_cash_flow",
        )

        shares_outstanding = self._validate_finite(
            shares_outstanding,
            "shares_outstanding",
        )

        # -----------------------------------------------------
        # Shares must be positive.
        #
        # Zero would cause division by zero.
        # Negative shares are not financially meaningful.
        # -----------------------------------------------------

        if shares_outstanding <= 0.0:
            raise ValueError(
                "shares_outstanding must be greater than zero. "
                f"Got {shares_outstanding!r}."
            )

        # =====================================================
        # Project cash flows
        # =====================================================

        cashflows = self.project_cashflows(
            initial_fcf=free_cash_flow,
            years=5,
        )

        if not cashflows:
            raise ValueError(
                "DCF calculation requires at least one projected "
                "cash flow."
            )

        # =====================================================
        # Present value of projected cash flows
        # =====================================================

        pv_cashflows = self.calculate_present_value(
            cashflows
        )

        pv_cashflows = self._validate_finite(
            pv_cashflows,
            "pv_cashflows",
        )

        # =====================================================
        # Terminal value
        # =====================================================

        final_cashflow = cashflows[-1]

        final_cashflow = self._validate_finite(
            final_cashflow,
            "final_cashflow",
        )

        terminal_value = self.calculate_terminal_value(
            final_cashflow
        )

        terminal_value = self._validate_finite(
            terminal_value,
            "terminal_value",
        )

        # =====================================================
        # Discount terminal value
        # =====================================================

        discount_base = 1.0 + self.discount_rate

        discount_base = self._validate_finite(
            discount_base,
            "terminal_discount_base",
        )

        if discount_base <= 0.0:
            raise ValueError(
                "1 + discount_rate must be greater than zero."
            )

        try:
            terminal_discount_factor = (
                discount_base ** len(cashflows)
            )
        except (OverflowError, ValueError) as exc:
            raise ValueError(
                "Terminal value discount factor became invalid."
            ) from exc

        terminal_discount_factor = self._validate_finite(
            terminal_discount_factor,
            "terminal_discount_factor",
        )

        if terminal_discount_factor == 0.0:
            raise ValueError(
                "Terminal value discount factor cannot be zero."
            )

        discounted_terminal_value = (
            terminal_value
            / terminal_discount_factor
        )

        discounted_terminal_value = self._validate_finite(
            discounted_terminal_value,
            "discounted_terminal_value",
        )

        # =====================================================
        # Enterprise Value
        # =====================================================

        enterprise_value = (
            pv_cashflows
            + discounted_terminal_value
        )

        enterprise_value = self._validate_finite(
            enterprise_value,
            "enterprise_value",
        )

        # =====================================================
        # Equity Value
        # =====================================================

        # This model currently assumes:
        #
        #     Equity Value = Enterprise Value
        #
        # Debt, cash, minority interest, etc. can be incorporated
        # later if the DCFResult contract is expanded.

        equity_value = enterprise_value

        equity_value = self._validate_finite(
            equity_value,
            "equity_value",
        )

        # =====================================================
        # Fair Value Per Share
        # =====================================================

        fair_value = (
            equity_value
            / shares_outstanding
        )

        fair_value = self._validate_finite(
            fair_value,
            "fair_value_per_share",
        )

        # =====================================================
        # Build assumptions
        # =====================================================

        assumptions = {
            "growth_rate": self.growth_rate,
            "discount_rate": self.discount_rate,
            "terminal_growth": self.terminal_growth,
        }

        # Validate assumptions before constructing the result.
        for name, value in assumptions.items():
            self._validate_finite(
                value,
                f"assumption.{name}",
            )

        # =====================================================
        # Final DCFResult
        # =====================================================

        result = DCFResult(
            enterprise_value=enterprise_value,
            equity_value=equity_value,
            fair_value_per_share=fair_value,
            assumptions=assumptions,
        )

        # -----------------------------------------------------
        # Final safety boundary
        #
        # Even though every calculation above has been validated,
        # verify the final numeric fields one more time before
        # allowing them to leave this model.
        # -----------------------------------------------------

        self._validate_finite(
            result.enterprise_value,
            "result.enterprise_value",
        )

        self._validate_finite(
            result.equity_value,
            "result.equity_value",
        )

        self._validate_finite(
            result.fair_value_per_share,
            "result.fair_value_per_share",
        )

        return result

    # =========================================================
    # Numeric Validation
    # =========================================================

    @staticmethod
    def _validate_finite(
        value: float,
        field_name: str,
    ) -> float:
        """
        Validate and normalize a numeric DCF value.

        Rejects:

            None
            non-numeric values
            NaN
            +inf
            -inf

        Returns a regular Python float.

        This method is intentionally used throughout the DCF
        calculation so invalid values are rejected at their source
        instead of reaching AgentResult / JSON serialization.
        """

        # -----------------------------------------------------
        # Reject booleans.
        #
        # bool is a subclass of int in Python, but True/False are
        # not meaningful financial values.
        # -----------------------------------------------------

        if isinstance(value, bool):
            raise TypeError(
                f"{field_name} must be a finite numeric value, "
                "not bool."
            )

        try:
            numeric_value = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise TypeError(
                f"{field_name} must be a finite numeric value. "
                f"Got {value!r}."
            ) from exc

        # -----------------------------------------------------
        # Reject NaN and infinities.
        # -----------------------------------------------------

        if not math.isfinite(numeric_value):
            if math.isnan(numeric_value):
                raise ValueError(
                    f"{field_name} cannot be NaN."
                )

            raise ValueError(
                f"{field_name} must be finite. "
                f"Got {numeric_value!r}."
            )

        return numeric_value