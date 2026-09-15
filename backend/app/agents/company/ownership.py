
"""
app/agents/company/ownership.py

Analyzes company ownership structure.

Responsibility:
    - Consume researched ownership facts.
    - Normalize ownership data.
    - Derive ownership concentration and control indicators.
    - Identify potential ownership-related risks.

This class does NOT perform external research or retrieval.
"""

from __future__ import annotations

from typing import Any, Dict, List


class OwnershipAnalyzer:
    """
    Analyzes the ownership structure of a company.

    Expected researched input may contain:

        major_shareholders
        institutional_ownership
        insider_ownership
        founder_control
        ownership_structure

    The research/retrieval layer is responsible for discovering
    these facts.
    """

    def analyze(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze researched ownership data.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary"
            )

        # =====================================================
        # Researched facts
        # =====================================================

        major_shareholders = self._as_list(
            data.get("major_shareholders")
        )

        institutional_ownership = data.get(
            "institutional_ownership"
        )

        insider_ownership = data.get(
            "insider_ownership"
        )

        founder_control = data.get(
            "founder_control"
        )

        ownership_structure = data.get(
            "ownership_structure"
        )

        # =====================================================
        # Derived analysis
        # =====================================================

        shareholder_count = len(
            major_shareholders
        )

        ownership_concentration = (
            self._assess_ownership_concentration(
                major_shareholders
            )
        )

        institutional_assessment = (
            self._assess_institutional_ownership(
                institutional_ownership
            )
        )

        insider_assessment = (
            self._assess_insider_ownership(
                insider_ownership
            )
        )

        founder_control_assessment = (
            self._assess_founder_control(
                founder_control
            )
        )

        control_characteristics = (
            self._identify_control_characteristics(
                institutional_ownership=(
                    institutional_ownership
                ),
                insider_ownership=(
                    insider_ownership
                ),
                founder_control=founder_control,
                ownership_structure=(
                    ownership_structure
                ),
            )
        )

        ownership_risks = (
            self._identify_ownership_risks(
                major_shareholders=major_shareholders,
                institutional_ownership=(
                    institutional_ownership
                ),
                insider_ownership=(
                    insider_ownership
                ),
                founder_control=founder_control,
                ownership_structure=(
                    ownership_structure
                ),
            )
        )

        return {
            # -------------------------------------------------
            # Researched facts
            # -------------------------------------------------

            "major_shareholders": (
                major_shareholders
            ),

            "institutional_ownership": (
                institutional_ownership
            ),

            "insider_ownership": (
                insider_ownership
            ),

            "founder_control": (
                founder_control
            ),

            "ownership_structure": (
                ownership_structure
            ),

            # -------------------------------------------------
            # Derived metrics
            # -------------------------------------------------

            "major_shareholder_count": (
                shareholder_count
            ),

            "ownership_concentration": (
                ownership_concentration
            ),

            # -------------------------------------------------
            # Ownership analysis
            # -------------------------------------------------

            "institutional_assessment": (
                institutional_assessment
            ),

            "insider_assessment": (
                insider_assessment
            ),

            "founder_control_assessment": (
                founder_control_assessment
            ),

            "control_characteristics": (
                control_characteristics
            ),

            "ownership_risks": ownership_risks,

            "analysis_status": "completed",
        }

    # =========================================================
    # Normalization
    # =========================================================

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        """
        Normalize list-like ownership data.
        """

        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, tuple):
            return list(value)

        return [value]

    # =========================================================
    # Ownership Concentration
    # =========================================================

    @staticmethod
    def _assess_ownership_concentration(
        major_shareholders: List[Any],
    ) -> str:
        """
        Provide a structural assessment of ownership
        concentration.

        This does not calculate actual ownership percentages
        unless the research layer supplies them.
        """

        count = len(major_shareholders)

        if count == 0:
            return "unknown"

        if count == 1:
            return "potentially_high"

        if count <= 3:
            return "potentially_moderate_to_high"

        if count <= 10:
            return "moderate"

        return "broad"

    # =========================================================
    # Institutional Ownership
    # =========================================================

    @staticmethod
    def _assess_institutional_ownership(
        institutional_ownership: Any,
    ) -> str:
        """
        Interpret institutional ownership when a percentage
        or qualitative value is available.
        """

        if institutional_ownership is None:
            return "unknown"

        percentage = (
            OwnershipAnalyzer._percentage_value(
                institutional_ownership
            )
        )

        if percentage is not None:

            if percentage >= 70:
                return "high"

            if percentage >= 40:
                return "moderate"

            return "low"

        if isinstance(
            institutional_ownership,
            str,
        ):
            return institutional_ownership

        return "available"

    # =========================================================
    # Insider Ownership
    # =========================================================

    @staticmethod
    def _assess_insider_ownership(
        insider_ownership: Any,
    ) -> str:
        """
        Interpret insider ownership when a percentage
        or qualitative value is available.
        """

        if insider_ownership is None:
            return "unknown"

        percentage = (
            OwnershipAnalyzer._percentage_value(
                insider_ownership
            )
        )

        if percentage is not None:

            if percentage >= 20:
                return "high"

            if percentage >= 5:
                return "moderate"

            return "low"

        if isinstance(
            insider_ownership,
            str,
        ):
            return insider_ownership

        return "available"

    # =========================================================
    # Founder Control
    # =========================================================

    @staticmethod
    def _assess_founder_control(
        founder_control: Any,
    ) -> str:
        """
        Interpret founder-control information.

        This supports boolean, numeric and qualitative values.
        """

        if founder_control is None:
            return "unknown"

        if isinstance(
            founder_control,
            bool,
        ):
            return (
                "present"
                if founder_control
                else "absent"
            )

        percentage = (
            OwnershipAnalyzer._percentage_value(
                founder_control
            )
        )

        if percentage is not None:

            if percentage >= 50:
                return "controlling"

            if percentage >= 20:
                return "significant"

            if percentage > 0:
                return "minor"

            return "absent"

        return str(founder_control)

    # =========================================================
    # Control Characteristics
    # =========================================================

    @staticmethod
    def _identify_control_characteristics(
        institutional_ownership: Any,
        insider_ownership: Any,
        founder_control: Any,
        ownership_structure: Any,
    ) -> List[str]:
        """
        Identify important ownership/control characteristics.

        These are analytical flags rather than definitive
        governance conclusions.
        """

        characteristics: List[str] = []

        founder_assessment = (
            OwnershipAnalyzer._assess_founder_control(
                founder_control
            )
        )

        if founder_assessment in {
            "controlling",
            "significant",
            "present",
        }:
            characteristics.append(
                "Founder influence may be material"
            )

        institutional_assessment = (
            OwnershipAnalyzer._assess_institutional_ownership(
                institutional_ownership
            )
        )

        if institutional_assessment == "high":
            characteristics.append(
                "Institutional ownership appears significant"
            )

        insider_assessment = (
            OwnershipAnalyzer._assess_insider_ownership(
                insider_ownership
            )
        )

        if insider_assessment == "high":
            characteristics.append(
                "Insider ownership appears significant"
            )

        if isinstance(
            ownership_structure,
            str,
        ):
            structure = (
                ownership_structure.lower()
            )

            if "dual class" in structure:
                characteristics.append(
                    "Dual-class ownership structure"
                )

            if "family controlled" in structure:
                characteristics.append(
                    "Family-controlled ownership structure"
                )

            if "founder controlled" in structure:
                characteristics.append(
                    "Founder-controlled ownership structure"
                )

        return characteristics

    # =========================================================
    # Ownership Risks
    # =========================================================

    @staticmethod
    def _identify_ownership_risks(
        major_shareholders: List[Any],
        institutional_ownership: Any,
        insider_ownership: Any,
        founder_control: Any,
        ownership_structure: Any,
    ) -> List[str]:
        """
        Identify potential ownership-related risks.
        """

        risks: List[str] = []

        # -----------------------------------------------------
        # Concentration
        # -----------------------------------------------------

        concentration = (
            OwnershipAnalyzer._assess_ownership_concentration(
                major_shareholders
            )
        )

        if concentration in {
            "potentially_high",
            "potentially_moderate_to_high",
        }:
            risks.append(
                "Potential shareholder concentration risk"
            )

        # -----------------------------------------------------
        # Founder control
        # -----------------------------------------------------

        founder_assessment = (
            OwnershipAnalyzer._assess_founder_control(
                founder_control
            )
        )

        if founder_assessment == "controlling":
            risks.append(
                "Potential controlling-shareholder risk"
            )

        # -----------------------------------------------------
        # High insider ownership
        # -----------------------------------------------------

        insider_assessment = (
            OwnershipAnalyzer._assess_insider_ownership(
                insider_ownership
            )
        )

        if insider_assessment == "high":
            risks.append(
                "Potential insider-control or alignment risk"
            )

        # -----------------------------------------------------
        # Dual-class structures
        # -----------------------------------------------------

        if isinstance(
            ownership_structure,
            str,
        ):
            structure = (
                ownership_structure.lower()
            )

            if "dual class" in structure:
                risks.append(
                    "Potential voting-rights concentration "
                    "from dual-class structure"
                )

        return risks

    # =========================================================
    # Percentage Parsing
    # =========================================================

    @staticmethod
    def _percentage_value(
        value: Any,
    ) -> float | None:
        """
        Convert common percentage representations to a
        numeric percentage.

        Examples:

            25       -> 25.0
            0.25     -> 25.0
            "25%"    -> 25.0
            "25"     -> 25.0

        Returns None when the value cannot be interpreted.
        """

        if isinstance(
            value,
            bool,
        ):
            return None

        if isinstance(
            value,
            (int, float),
        ):
            number = float(value)

            if 0 <= number <= 1:
                return number * 100

            if 0 <= number <= 100:
                return number

            return None

        if isinstance(
            value,
            str,
        ):
            cleaned = (
                value
                .strip()
                .replace("%", "")
                .replace(",", "")
            )

            try:
                number = float(cleaned)
            except ValueError:
                return None

            if 0 <= number <= 1:
                return number * 100

            if 0 <= number <= 100:
                return number

        return None

