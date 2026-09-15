
"""
app/agents/company/business_model.py

Analyzes how a company creates, delivers, and captures value.

Responsibility:
    - Consume researched business-model facts.
    - Analyze revenue model and customer structure.
    - Analyze supplier dependencies.
    - Assess competitive advantages.
    - Identify potential business-model risks.

This class does NOT perform external research or retrieval.
"""

from __future__ import annotations

from typing import Any, Dict, List


class BusinessModelAnalyzer:
    """
    Analyzes how a company creates and captures value.

    Expected researched input may contain:

        revenue_model
        products_services
        customer_segments
        geography
        key_suppliers
        competitive_advantages
        business_risks

    The research/retrieval layer is responsible for discovering
    these facts.
    """

    def analyze(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze researched business-model data.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary"
            )

        # =====================================================
        # Researched facts
        # =====================================================

        revenue_model = data.get(
            "revenue_model"
        )

        products_services = self._as_list(
            data.get("products_services")
        )

        customer_segments = self._as_list(
            data.get("customer_segments")
        )

        geography = self._as_list(
            data.get("geography")
        )

        key_suppliers = self._as_list(
            data.get("key_suppliers")
        )

        competitive_advantages = self._as_list(
            data.get(
                "competitive_advantages"
            )
        )

        business_risks = self._as_list(
            data.get("business_risks")
        )

        # =====================================================
        # Derived analysis
        # =====================================================

        revenue_model_assessment = (
            self._assess_revenue_model(
                revenue_model
            )
        )

        offering_breadth = (
            self._assess_offering_breadth(
                products_services
            )
        )

        customer_diversification = (
            self._assess_customer_diversification(
                customer_segments
            )
        )

        supplier_dependency = (
            self._assess_supplier_dependency(
                key_suppliers
            )
        )

        competitive_position = (
            self._assess_competitive_position(
                competitive_advantages
            )
        )

        business_model_strength = (
            self._assess_business_model_strength(
                revenue_model=revenue_model,
                products_services=(
                    products_services
                ),
                customer_segments=(
                    customer_segments
                ),
                competitive_advantages=(
                    competitive_advantages
                ),
            )
        )

        business_model_risks = (
            self._identify_business_model_risks(
                revenue_model=revenue_model,
                customer_segments=(
                    customer_segments
                ),
                geography=geography,
                key_suppliers=key_suppliers,
                competitive_advantages=(
                    competitive_advantages
                ),
                business_risks=business_risks,
            )
        )

        # =====================================================
        # Result
        # =====================================================

        return {
            # -------------------------------------------------
            # Researched facts
            # -------------------------------------------------

            "revenue_model": revenue_model,

            "products_services": (
                products_services
            ),

            "customer_segments": (
                customer_segments
            ),

            "geography": geography,

            "key_suppliers": key_suppliers,

            "competitive_advantages": (
                competitive_advantages
            ),

            "business_risks": business_risks,

            # -------------------------------------------------
            # Derived metrics
            # -------------------------------------------------

            "product_service_count": (
                len(products_services)
            ),

            "customer_segment_count": (
                len(customer_segments)
            ),

            "supplier_count": (
                len(key_suppliers)
            ),

            "competitive_advantage_count": (
                len(competitive_advantages)
            ),

            # -------------------------------------------------
            # Business model analysis
            # -------------------------------------------------

            "revenue_model_assessment": (
                revenue_model_assessment
            ),

            "offering_breadth": (
                offering_breadth
            ),

            "customer_diversification": (
                customer_diversification
            ),

            "supplier_dependency": (
                supplier_dependency
            ),

            "competitive_position": (
                competitive_position
            ),

            "business_model_strength": (
                business_model_strength
            ),

            "business_model_risks": (
                business_model_risks
            ),

            "analysis_status": "completed",
        }

    # =========================================================
    # Normalization
    # =========================================================

    @staticmethod
    def _as_list(
        value: Any,
    ) -> List[Any]:
        """
        Normalize list-like business-model data.
        """

        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, tuple):
            return list(value)

        return [value]

    # =========================================================
    # Revenue Model
    # =========================================================

    @staticmethod
    def _assess_revenue_model(
        revenue_model: Any,
    ) -> str:
        """
        Classify the available revenue model information.

        This describes the model; it does not claim the model
        is economically superior.
        """

        if revenue_model is None:
            return "unknown"

        if isinstance(
            revenue_model,
            dict,
        ):
            model_type = (
                revenue_model.get("type")
                or revenue_model.get("model")
            )

            if model_type:
                return str(model_type)

            return "structured_information_available"

        return str(revenue_model)

    # =========================================================
    # Offering Breadth
    # =========================================================

    @staticmethod
    def _assess_offering_breadth(
        products_services: List[Any],
    ) -> str:
        """
        Assess the breadth of products and services.
        """

        count = len(products_services)

        if count == 0:
            return "unknown"

        if count <= 2:
            return "narrow"

        if count <= 5:
            return "moderate"

        return "broad"

    # =========================================================
    # Customer Diversification
    # =========================================================

    @staticmethod
    def _assess_customer_diversification(
        customer_segments: List[Any],
    ) -> str:
        """
        Assess customer diversification based on the number
        of identified customer segments.

        This does not measure actual revenue concentration.
        """

        count = len(customer_segments)

        if count == 0:
            return "unknown"

        if count == 1:
            return "low"

        if count <= 3:
            return "moderate"

        return "high"

    # =========================================================
    # Supplier Dependency
    # =========================================================

    @staticmethod
    def _assess_supplier_dependency(
        key_suppliers: List[Any],
    ) -> str:
        """
        Assess potential supplier concentration.

        Actual dependency requires purchasing/spend data, so
        this is a structural assessment only.
        """

        count = len(key_suppliers)

        if count == 0:
            return "unknown"

        if count == 1:
            return "potentially_high"

        if count <= 3:
            return "potentially_moderate"

        return "diversified"

    # =========================================================
    # Competitive Position
    # =========================================================

    @staticmethod
    def _assess_competitive_position(
        competitive_advantages: List[Any],
    ) -> str:
        """
        Assess the breadth of identified competitive advantages.

        The presence of listed advantages does not independently
        prove that those advantages are durable.
        """

        count = len(
            competitive_advantages
        )

        if count == 0:
            return "unknown"

        if count == 1:
            return "limited_information"

        if count <= 3:
            return "moderate"

        return "broad"

    # =========================================================
    # Business Model Strength
    # =========================================================

    @staticmethod
    def _assess_business_model_strength(
        revenue_model: Any,
        products_services: List[Any],
        customer_segments: List[Any],
        competitive_advantages: List[Any],
    ) -> str:
        """
        Provide a structural assessment of business-model
        information completeness.

        This is NOT a profitability or investment rating.
        """

        information_points = 0

        if revenue_model:
            information_points += 1

        if products_services:
            information_points += 1

        if customer_segments:
            information_points += 1

        if competitive_advantages:
            information_points += 1

        if information_points == 0:
            return "insufficient_information"

        if information_points <= 2:
            return "partially_defined"

        if information_points == 3:
            return "well_defined"

        return "strongly_defined"

    # =========================================================
    # Business Model Risks
    # =========================================================

    @staticmethod
    def _identify_business_model_risks(
        revenue_model: Any,
        customer_segments: List[Any],
        geography: List[Any],
        key_suppliers: List[Any],
        competitive_advantages: List[Any],
        business_risks: List[Any],
    ) -> List[str]:
        """
        Identify potential business-model risks.

        These are flags for further research rather than
        definitive investment conclusions.
        """

        risks: List[str] = []

        # -----------------------------------------------------
        # Revenue model
        # -----------------------------------------------------

        if not revenue_model:
            risks.append(
                "Revenue model information unavailable"
            )

        # -----------------------------------------------------
        # Customer concentration
        # -----------------------------------------------------

        if len(customer_segments) == 1:
            risks.append(
                "Potential customer-segment concentration"
            )

        elif len(customer_segments) == 0:
            risks.append(
                "Customer-segment information unavailable"
            )

        # -----------------------------------------------------
        # Supplier concentration
        # -----------------------------------------------------

        if len(key_suppliers) == 1:
            risks.append(
                "Potential dependence on a key supplier"
            )

        # -----------------------------------------------------
        # Geographic exposure
        # -----------------------------------------------------

        if len(geography) == 1:
            risks.append(
                "Potential geographic concentration"
            )

        # -----------------------------------------------------
        # Competitive moat information
        # -----------------------------------------------------

        if not competitive_advantages:
            risks.append(
                "Competitive-advantage information unavailable"
            )

        # -----------------------------------------------------
        # Existing researched risks
        # -----------------------------------------------------

        for risk in business_risks:

            if risk and risk not in risks:
                risks.append(risk)

        return risks

