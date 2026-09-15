from typing import Dict


class IntentParser:
    """
    Converts a user's query into a structured intent.
    Later this will use an LLM.
    """

    def parse(self, query: str) -> Dict:
        query_lower = query.lower()

        if any(word in query_lower for word in ["latest", "news", "recent"]):
            intent = "news"

        elif any(word in query_lower for word in ["compare", "vs"]):
            intent = "comparison"

        elif any(word in query_lower for word in ["summarize", "summary"]):
            intent = "summary"

        else:
            intent = "general"

        return {
    "intent": intent,
    "query": query,
    "requires_search": intent in ["news", "comparison"],
    "requires_summary": intent == "summary"
}