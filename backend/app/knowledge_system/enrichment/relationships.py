from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from app.knowledge_system.types import KnowledgeItem


logger = logging.getLogger(__name__)


class RelationshipExtractor:
    """
    Extract relationships between entities.

    Creates knowledge graph edges.

    Example:

    {
        "source": "Apple Inc",
        "relation": "produces",
        "target": "iPhone",
        "confidence": 0.92
    }
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
                relationships = await self._llm_extract(
                    item
                )

            else:
                relationships = self._rule_based_extract(
                    item
                )


            return [
                self.normalize_relationship(r)
                for r in relationships
            ]


        except Exception:

            logger.exception(
                "Relationship extraction failed"
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
You are a knowledge graph extraction system.

Analyze this knowledge:

{content}


Extract relationships between entities.

Return ONLY JSON:

[
 {{
   "source": "entity",
   "relation": "relationship",
   "target": "entity",
   "confidence": 0.0
 }}
]

Rules:

- relation must describe the connection
- confidence between 0 and 1
- ignore weak relationships
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

        relationships = []


        entities = getattr(
            item,
            "entities",
            []
        )


        if not entities:
            return []


        names = []


        for entity in entities:

            if isinstance(entity, str):
                names.append(entity)

            elif isinstance(entity, dict):
                names.append(
                    entity.get(
                        "name"
                    )
                )


        names = [
            n for n in names
            if n
        ]


        for index in range(
            len(names)-1
        ):

            relationships.append(
                {
                    "source": names[index],
                    "relation": "related_to",
                    "target": names[index+1],
                    "confidence": 0.25
                }
            )


        return relationships



    def _parse_response(
        self,
        response: Any,
    ) -> List[Dict[str, Any]]:


        try:

            if isinstance(response, list):
                return response


            if isinstance(response, str):

                return json.loads(
                    response
                )


            if isinstance(response, dict):

                # OpenAI/OpenRouter format

                if "choices" in response:

                    content = (
                        response["choices"][0]
                        ["message"]
                        ["content"]
                    )

                    return json.loads(
                        content
                    )


                return response.get(
                    "relationships",
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
                "Relationship parsing failed: %s",
                e
            )


        return []



    def normalize_relationship(
        self,
        relationship: Dict[str, Any],
    ) -> Dict[str, Any]:


        source = relationship.get(
            "source"
        )

        target = relationship.get(
            "target"
        )


        if not source or not target:

            return {}


        return {

            "source": str(source),

            "relation": relationship.get(
                "relation",
                "related_to"
            ),

            "target": str(target),

            "confidence": max(
                0.0,
                min(
                    1.0,
                    float(
                        relationship.get(
                            "confidence",
                            0.0
                        )
                    )
                )
            )

        }