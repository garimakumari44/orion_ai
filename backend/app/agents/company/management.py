
"""
app/agents/company/management.py

Analyzes company leadership and governance.

Responsibility:
    - Consume researched management facts.
    - Normalize leadership data.
    - Derive basic management and governance insights.
    - Identify potential leadership risks.

This class does NOT perform external research or retrieval.
"""

from __future__ import annotations

from typing import Any, Dict, List


class ManagementAnalyzer:
    """
    Analyzes company leadership and governance.

    Expected researched input may contain:

        ceo
        executives
        board_members
        leadership_quality
        management_notes
        governance_rating

    The research/retrieval layer is responsible for discovering
    these facts.
    """

    def analyze(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze researched management data.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary"
            )

        # =====================================================
        # Researched facts
        # =====================================================

        ceo = data.get("ceo")

        executives = self._as_list(
            data.get("executives")
        )

        board_members = self._as_list(
            data.get("board_members")
        )

        leadership_quality = data.get(
            "leadership_quality"
        )

        management_notes = data.get(
            "management_notes"
        )

        governance_rating = data.get(
            "governance_rating"
        )

        # =====================================================
        # Derived analysis
        # =====================================================

        executive_count = len(executives)

        board_member_count = len(
            board_members
        )

        leadership_depth = (
            self._assess_leadership_depth(
                ceo=ceo,
                executives=executives,
            )
        )

        board_depth = (
            self._assess_board_depth(
                board_members
            )
        )

        governance_assessment = (
            self._assess_governance(
                governance_rating=governance_rating,
                board_members=board_members,
            )
        )

        key_person_risk = (
            self._assess_key_person_risk(
                ceo=ceo,
                executives=executives,
            )
        )

        management_risks = (
            self._identify_management_risks(
                ceo=ceo,
                executives=executives,
                board_members=board_members,
                leadership_quality=leadership_quality,
                governance_rating=governance_rating,
            )
        )

        # =====================================================
        # Result
        # =====================================================

        return {
            # -------------------------------------------------
            # Researched facts
            # -------------------------------------------------

            "ceo": ceo,

            "executives": executives,

            "board_members": board_members,

            "leadership_quality": (
                leadership_quality
            ),

            "management_notes": (
                management_notes
            ),

            "governance_rating": (
                governance_rating
            ),

            # -------------------------------------------------
            # Derived metrics
            # -------------------------------------------------

            "executive_count": executive_count,

            "board_member_count": (
                board_member_count
            ),

            "leadership_depth": (
                leadership_depth
            ),

            "board_depth": board_depth,

            # -------------------------------------------------
            # Management analysis
            # -------------------------------------------------

            "governance_assessment": (
                governance_assessment
            ),

            "key_person_risk": (
                key_person_risk
            ),

            "management_risks": (
                management_risks
            ),

            "analysis_status": "completed",
        }

    # =========================================================
    # Normalization
    # =========================================================

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        """
        Normalize list-like management fields.

        Missing data becomes an empty list.

        No management facts are fabricated.
        """

        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, tuple):
            return list(value)

        return [value]

    # =========================================================
    # Leadership Depth
    # =========================================================

    @staticmethod
    def _assess_leadership_depth(
        ceo: Any,
        executives: List[Any],
    ) -> str:
        """
        Assess the apparent depth of the executive team.

        This is a structural heuristic only. It does not assess
        executive quality or competence.
        """

        if not ceo and not executives:
            return "unknown"

        if ceo and not executives:
            return "limited_information"

        if len(executives) <= 2:
            return "limited"

        if len(executives) <= 5:
            return "moderate"

        return "broad"

    # =========================================================
    # Board Depth
    # =========================================================

    @staticmethod
    def _assess_board_depth(
        board_members: List[Any],
    ) -> str:
        """
        Assess board information depth.

        This measures available board information, not
        board quality.
        """

        count = len(board_members)

        if count == 0:
            return "unknown"

        if count <= 3:
            return "limited"

        if count <= 8:
            return "moderate"

        return "broad"

    # =========================================================
    # Governance
    # =========================================================

    @staticmethod
    def _assess_governance(
        governance_rating: Any,
        board_members: List[Any],
    ) -> str:
        """
        Interpret an explicitly supplied governance rating.

        If no rating exists, provide a structural assessment
        without pretending to know governance quality.
        """

        if governance_rating is not None:

            if isinstance(
                governance_rating,
                (int, float),
            ):
                if governance_rating >= 8:
                    return "strong"

                if governance_rating >= 5:
                    return "moderate"

                return "weak"

            return str(
                governance_rating
            )

        if not board_members:
            return "insufficient_information"

        return "structurally_present"

    # =========================================================
    # Key Person Risk
    # =========================================================

    @staticmethod
    def _assess_key_person_risk(
        ceo: Any,
        executives: List[Any],
    ) -> str:
        """
        Assess potential key-person dependency using only
        the structure of the available leadership data.

        This is a preliminary heuristic.
        """

        if not ceo:
            return "unknown"

        if len(executives) == 0:
            return "potentially_high"

        if len(executives) <= 2:
            return "potentially_moderate"

        return "potentially_lower"

    # =========================================================
    # Management Risks
    # =========================================================

    @staticmethod
    def _identify_management_risks(
        ceo: Any,
        executives: List[Any],
        board_members: List[Any],
        leadership_quality: Any,
        governance_rating: Any,
    ) -> List[str]:
        """
        Identify potential management and governance risks.

        These are flags for further research, not definitive
        conclusions.
        """

        risks: List[str] = []

        # -----------------------------------------------------
        # Missing CEO information
        # -----------------------------------------------------

        if not ceo:
            risks.append(
                "CEO information unavailable"
            )

        # -----------------------------------------------------
        # Limited executive information
        # -----------------------------------------------------

        if len(executives) == 0:
            risks.append(
                "Limited executive leadership information"
            )

        # -----------------------------------------------------
        # Limited board information
        # -----------------------------------------------------

        if len(board_members) == 0:
            risks.append(
                "Board composition information unavailable"
            )

        # -----------------------------------------------------
        # Leadership quality
        # -----------------------------------------------------

        if isinstance(
            leadership_quality,
            str,
        ):
            quality = (
                leadership_quality.lower()
            )

            if quality in {
                "weak",
                "poor",
                "low",
            }:
                risks.append(
                    "Potential leadership-quality concern"
                )

        # -----------------------------------------------------
        # Governance rating
        # -----------------------------------------------------

        if isinstance(
            governance_rating,
            str,
        ):
            rating = (
                governance_rating.lower()
            )

            if rating in {
                "weak",
                "poor",
                "low",
            }:
                risks.append(
                    "Potential governance concern"
                )

        elif isinstance(
            governance_rating,
            (int, float),
        ):
            if governance_rating < 5:
                risks.append(
                    "Potential governance concern"
                )

        return risks

