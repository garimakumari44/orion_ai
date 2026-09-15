
"""
app/agents/company/products.py

Analyzes a company's products and services.

Responsibility:
    - Consume researched product and service facts.
    - Normalize product information.
    - Analyze product portfolio breadth and diversification.
    - Identify key-product and portfolio concentration signals.
    - Identify potential product-related risks.

This class does NOT perform external research or retrieval.
"""

from __future__ import annotations

from typing import Any, Dict, List


class ProductAnalyzer:
    """
    Analyzes a company's products and services.

    Expected researched input may contain:

        products
        services
        platforms
        product_categories
        key_products
        product_strengths

    The research/retrieval layer is responsible for discovering
    these facts.
    """

    def analyze(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze researched product and service data.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary"
            )

        # =====================================================
        # Researched facts
        # =====================================================

        products = self._as_list(
            data.get("products")
        )

        services = self._as_list(
            data.get("services")
        )

        platforms = self._as_list(
            data.get("platforms")
        )

        product_categories = self._as_list(
            data.get("product_categories")
        )

        key_products = self._as_list(
            data.get("key_products")
        )

        product_strengths = self._as_list(
            data.get("product_strengths")
        )

        # =====================================================
        # Derived analysis
        # =====================================================

        product_count = len(products)

        service_count = len(services)

        platform_count = len(platforms)

        category_count = len(
            product_categories
        )

        key_product_count = len(
            key_products
        )

        portfolio_breadth = (
            self._assess_portfolio_breadth(
                product_count=product_count,
                service_count=service_count,
                platform_count=platform_count,
                category_count=category_count,
            )
        )

        portfolio_diversification = (
            self._assess_portfolio_diversification(
                category_count=category_count,
                product_count=product_count,
                service_count=service_count,
            )
        )

        product_concentration = (
            self._assess_product_concentration(
                products=products,
                key_products=key_products,
                product_categories=(
                    product_categories
                ),
            )
        )

        platform_dependency = (
            self._assess_platform_dependency(
                platforms=platforms,
                products=products,
                services=services,
            )
        )

        product_mix = (
            self._classify_product_mix(
                products=products,
                services=services,
                platforms=platforms,
            )
        )

        product_risks = (
            self._identify_product_risks(
                products=products,
                services=services,
                platforms=platforms,
                product_categories=(
                    product_categories
                ),
                key_products=key_products,
            )
        )

        return {
            # -------------------------------------------------
            # Researched facts
            # -------------------------------------------------

            "products": products,

            "services": services,

            "platforms": platforms,

            "product_categories": (
                product_categories
            ),

            "key_products": key_products,

            "product_strengths": (
                product_strengths
            ),

            # -------------------------------------------------
            # Derived metrics
            # -------------------------------------------------

            "product_count": product_count,

            "service_count": service_count,

            "platform_count": platform_count,

            "product_category_count": (
                category_count
            ),

            "key_product_count": (
                key_product_count
            ),

            # -------------------------------------------------
            # Product portfolio analysis
            # -------------------------------------------------

            "portfolio_breadth": (
                portfolio_breadth
            ),

            "portfolio_diversification": (
                portfolio_diversification
            ),

            "product_concentration": (
                product_concentration
            ),

            "platform_dependency": (
                platform_dependency
            ),

            "product_mix": product_mix,

            "product_risks": product_risks,

            "analysis_status": "completed",
        }

    # =========================================================
    # Normalization
    # =========================================================

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        """
        Normalize list-like product data.
        """

        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, tuple):
            return list(value)

        return [value]

    # =========================================================
    # Portfolio Breadth
    # =========================================================

    @staticmethod
    def _assess_portfolio_breadth(
        product_count: int,
        service_count: int,
        platform_count: int,
        category_count: int,
    ) -> str:
        """
        Assess the breadth of the available product portfolio.

        This is based only on the amount of product information
        supplied by the research layer.
        """

        total_offerings = (
            product_count
            + service_count
            + platform_count
        )

        if total_offerings == 0:
            return "unknown"

        if (
            total_offerings <= 2
            and category_count <= 1
        ):
            return "narrow"

        if (
            total_offerings <= 6
            and category_count <= 3
        ):
            return "moderate"

        return "broad"

    # =========================================================
    # Portfolio Diversification
    # =========================================================

    @staticmethod
    def _assess_portfolio_diversification(
        category_count: int,
        product_count: int,
        service_count: int,
    ) -> str:
        """
        Assess portfolio diversification.

        Category count is given greater weight than raw product
        count because many products can belong to one category.
        """

        if (
            category_count == 0
            and product_count == 0
            and service_count == 0
        ):
            return "unknown"

        if category_count <= 1:
            return "low"

        if category_count <= 3:
            return "moderate"

        return "high"

    # =========================================================
    # Product Concentration
    # =========================================================

    @staticmethod
    def _assess_product_concentration(
        products: List[Any],
        key_products: List[Any],
        product_categories: List[Any],
    ) -> str:
        """
        Identify potential product concentration.

        Actual revenue concentration requires financial data and
        is intentionally not inferred here.
        """

        if not products and not key_products:
            return "unknown"

        if len(key_products) == 1:
            return "potentially_high"

        if (
            len(key_products) > 1
            and len(product_categories) <= 1
        ):
            return "potentially_moderate_to_high"

        if len(product_categories) <= 2:
            return "moderate"

        return "diversified"

    # =========================================================
    # Platform Dependency
    # =========================================================

    @staticmethod
    def _assess_platform_dependency(
        platforms: List[Any],
        products: List[Any],
        services: List[Any],
    ) -> str:
        """
        Assess whether the company appears to have a
        platform-oriented business model.

        This does not establish economic dependency.
        """

        if not platforms:
            return "none_identified"

        if len(platforms) == 1:
            return "potentially_high"

        if len(platforms) <= 3:
            return "moderate"

        return "broad"

    # =========================================================
    # Product Mix
    # =========================================================

    @staticmethod
    def _classify_product_mix(
        products: List[Any],
        services: List[Any],
        platforms: List[Any],
    ) -> Dict[str, Any]:
        """
        Describe the structure of the product portfolio.
        """

        product_count = len(products)
        service_count = len(services)
        platform_count = len(platforms)

        total = (
            product_count
            + service_count
            + platform_count
        )

        if total == 0:
            return {
                "type": "unknown",
                "product_share": None,
                "service_share": None,
                "platform_share": None,
            }

        return {
            "type": ProductAnalyzer._determine_mix_type(
                product_count=product_count,
                service_count=service_count,
                platform_count=platform_count,
            ),
            "product_share": (
                product_count / total
            ),
            "service_share": (
                service_count / total
            ),
            "platform_share": (
                platform_count / total
            ),
        }

    @staticmethod
    def _determine_mix_type(
        product_count: int,
        service_count: int,
        platform_count: int,
    ) -> str:
        """
        Determine the dominant offering type.
        """

        values = {
            "products": product_count,
            "services": service_count,
            "platforms": platform_count,
        }

        non_zero = [
            key
            for key, value in values.items()
            if value > 0
        ]

        if len(non_zero) == 1:
            return non_zero[0]

        return "mixed"

    # =========================================================
    # Product Risks
    # =========================================================

    @staticmethod
    def _identify_product_risks(
        products: List[Any],
        services: List[Any],
        platforms: List[Any],
        product_categories: List[Any],
        key_products: List[Any],
    ) -> List[str]:
        """
        Identify potential product portfolio risks.

        These are analytical flags for further research,
        not definitive conclusions.
        """

        risks: List[str] = []

        # -----------------------------------------------------
        # Limited portfolio
        # -----------------------------------------------------

        total_offerings = (
            len(products)
            + len(services)
            + len(platforms)
        )

        if total_offerings == 0:
            risks.append(
                "Product and service portfolio information unavailable"
            )

        # -----------------------------------------------------
        # Product concentration
        # -----------------------------------------------------

        if len(key_products) == 1:
            risks.append(
                "Potential dependence on a key product"
            )

        # -----------------------------------------------------
        # Category concentration
        # -----------------------------------------------------

        if (
            len(product_categories) == 1
            and total_offerings > 1
        ):
            risks.append(
                "Potential product-category concentration"
            )

        # -----------------------------------------------------
        # Platform dependency
        # -----------------------------------------------------

        if len(platforms) == 1:
            risks.append(
                "Potential dependence on a single platform"
            )

        return risks

