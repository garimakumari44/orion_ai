"""
Retrieval Agent prompt templates.

The Retrieval Agent prepares retrieval strategies for
equity research.

Responsibilities:
- Understand financial information needs.
- Rewrite ambiguous investment queries.
- Generate search plans.
- Select authoritative evidence.
- Rank retrieved information.
- Never analyze or answer investment questions.
"""

from textwrap import dedent
from typing import List


class RetrievalPrompts:
    """Prompt templates for the Retrieval Agent."""

    @staticmethod
    def system_prompt() -> str:
        return dedent(
            """
            You are an expert Equity Research Retrieval Agent.

            Your only responsibility is retrieving the best possible
            information for downstream analyst agents.

            Responsibilities

            - Understand investment-related queries.
            - Detect companies, tickers, industries and macro topics.
            - Rewrite ambiguous financial queries.
            - Generate high-quality search queries.
            - Identify missing information required.
            - Select authoritative sources.
            - Rank retrieved evidence.
            - Prefer primary financial documents.
            - Never perform analysis.
            - Never make investment recommendations.
            - Never invent information.

            Preferred sources include:

            - SEC filings
            - Company annual reports
            - Quarterly earnings
            - Investor presentations
            - Official press releases
            - Exchange filings
            - Financial statements
            - Industry reports
            - Economic releases
            - Trusted financial news

            Always return structured JSON.
            """
        ).strip()

    @staticmethod
    def query_rewrite_prompt(
        user_query: str,
    ) -> str:
        return dedent(
            f"""
            User Query

            {user_query}

            Rewrite the query to maximize financial retrieval quality.

            Tasks

            - Preserve user intent.
            - Detect company names.
            - Detect stock tickers.
            - Detect industries.
            - Detect countries.
            - Expand abbreviations.
            - Add important financial keywords.
            - Infer missing retrieval terms when obvious.
            - Identify requested time period.

            Return JSON.

            {{
                "rewritten_query": "",
                "intent": "",
                "company": "",
                "ticker": "",
                "industry": "",
                "country": "",
                "time_period": "",
                "keywords": [],
                "entities": []
            }}
            """
        ).strip()

    @staticmethod
    def context_selection_prompt(
        query: str,
        retrieved_chunks: List[str],
    ) -> str:

        chunks = "\n\n".join(
            f"Chunk {i+1}:\n{chunk}"
            for i, chunk in enumerate(retrieved_chunks)
        )

        return dedent(
            f"""
            User Query

            {query}

            ---------------------------------------

            Retrieved Context

            {chunks}

            ---------------------------------------

            Select only evidence directly useful for equity research.

            Remove

            - duplicated information
            - irrelevant information
            - opinion pieces
            - promotional content
            - outdated information
            - unsupported claims

            Prefer

            - financial metrics
            - earnings data
            - management commentary
            - regulatory filings
            - official announcements
            - market data
            - industry evidence

            Return JSON.

            {{
                "selected_chunks": [],
                "removed_chunks": [],
                "reasoning": "",
                "confidence": 0.0
            }}
            """
        ).strip()

    @staticmethod
    def retrieval_plan_prompt(
        query: str,
        available_sources: List[str],
    ) -> str:

        sources = "\n".join(f"- {s}" for s in available_sources)

        return dedent(
            f"""
            User Query

            {query}

            ---------------------------------------

            Available Sources

            {sources}

            ---------------------------------------

            Build the optimal retrieval strategy.

            Consider

            - latest earnings
            - SEC filings
            - financial statements
            - investor presentations
            - macroeconomic data
            - industry reports
            - recent news
            - historical performance

            Return JSON.

            {{
                "search_queries": [],
                "preferred_sources": [],
                "retrieval_order": [],
                "expected_information": [],
                "missing_information": []
            }}
            """
        ).strip()

    @staticmethod
    def ranking_prompt(
        query: str,
        documents: List[str],
    ) -> str:

        docs = "\n\n".join(
            f"Document {i+1}:\n{doc}"
            for i, doc in enumerate(documents)
        )

        return dedent(
            f"""
            User Query

            {query}

            ---------------------------------------

            Candidate Documents

            {docs}

            ---------------------------------------

            Rank documents by usefulness for equity research.

            Ranking Criteria

            1. Regulatory filings
            2. Official company disclosures
            3. Financial statements
            4. Earnings calls
            5. Investor presentations
            6. Trusted financial news
            7. Industry reports
            8. Other sources

            Return JSON.

            {{
                "ranking": [],
                "reasoning": "",
                "confidence": 0.0
            }}
            """
        ).strip()