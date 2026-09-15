from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.knowledge_system.types import KnowledgeItem


logger = logging.getLogger(__name__)


class FinancialFactExtractor:
    """
    Extracts structured financial facts from knowledge items.

    Supports:

    - SEC filings
    - Earnings transcripts
    - Company reports
    - Financial documents

    Creates normalized financial intelligence.
    """


    def __init__(
        self,
        llm_service: Optional[Any] = None,
    ):
        self.llm_service = llm_service



    async def extract(
        self,
        item: KnowledgeItem,
    ) -> List[Dict[str, Any]]:

        try:

            if self.llm_service:

                facts = await self._llm_extract(
                    item
                )

            else:

                facts = self._rule_based_extract(
                    item
                )


            return [
                self.normalize_fact(f)
                for f in facts
                if f
            ]


        except Exception:

            logger.exception(
                "Financial fact extraction failed"
            )

            return []



    async def _llm_extract(
        self,
        item: KnowledgeItem,
    ) -> List[Dict[str, Any]]:


        content = getattr(
            item,
            "content",
            ""
        )


        prompt = f"""

You are a financial intelligence extraction system.

Extract financial facts from this document:

{content}


Return ONLY JSON:

[
 {{
   "company": "",
   "metric": "",
   "value": "",
   "unit": "",
   "currency": "",
   "period": "",
   "source": "",
   "confidence": 0.0
 }}
]


Extract only factual financial information:

Examples:

Revenue
Net Income
EBITDA
EPS
Cash Flow
Debt
Assets
Liabilities
Growth Rate
Margins

"""


        response = await self.llm_service.generate(
            prompt=prompt
        )


        return self._parse_response(
            response
        )



    def _rule_based_extract(
        self,
        item: KnowledgeItem,
    ) -> List[Dict[str, Any]]:

        """
        Basic extraction without LLM.

        Useful for testing.
        """


        facts = []


        text = getattr(
            item,
            "content",
            ""
        )


        keywords = [
            "revenue",
            "net income",
            "ebitda",
            "cash flow",
            "debt",
            "assets"
        ]


        lower = text.lower()


        for keyword in keywords:

            if keyword in lower:

                facts.append(
                    {
                        "metric": keyword,
                        "value": None,
                        "confidence": 0.2
                    }
                )


        return facts



    def normalize_fact(
        self,
        fact: Dict[str, Any],
    ) -> Dict[str, Any]:


        return {

            "company":
                fact.get(
                    "company"
                ),

            "metric":
                fact.get(
                    "metric",
                    "unknown"
                ),


            "value":
                fact.get(
                    "value"
                ),


            "unit":
                fact.get(
                    "unit"
                ),


            "currency":
                fact.get(
                    "currency",
                    "USD"
                ),


            "period":
                fact.get(
                    "period"
                ),


            "source":
                fact.get(
                    "source",
                    "unknown"
                ),


            "confidence":
                max(
                    0.0,
                    min(
                        1.0,
                        float(
                            fact.get(
                                "confidence",
                                0.0
                            )
                        )
                    )
                )
        }



    def _parse_response(
        self,
        response: Any,
    ) -> List[Dict[str, Any]]:

        import json


        try:

            if isinstance(response, list):
                return response


            if isinstance(response, str):

                return json.loads(
                    response
                )


            if isinstance(response, dict):

                return response.get(
                    "facts",
                    []
                )


            if hasattr(
                response,
                "content"
            ):

                return json.loads(
                    response.content
                )


        except Exception as e:

            logger.warning(
                "Financial fact parsing failed: %s",
                e
            )


        return []