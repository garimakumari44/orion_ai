"""
research.py

Research recovery module.

Responsible for:
- generating research tasks
- collecting evidence
- preparing context for rewriting
"""

from dataclasses import dataclass
from typing import List, Dict, Optional



@dataclass
class ResearchTask:
    """
    Represents a research request.
    """

    query: str

    reason: str

    priority: str = "medium"



@dataclass
class Evidence:

    content: str

    source: Optional[str] = None



@dataclass
class ResearchOutput:

    query: str

    evidence: List[Evidence]



class ResearchPlanner:
    """
    Converts evaluation failures
    into research tasks.
    """



    def create_tasks(
        self,
        issues: List[str]
    ) -> List[ResearchTask]:


        tasks = []


        for issue in issues:


            issue_lower = (
                issue.lower()
            )


            if (
                "fact" in issue_lower
                or
                "incorrect" in issue_lower
            ):

                tasks.append(
                    ResearchTask(
                        query=issue,
                        reason="Verify factual accuracy",
                        priority="high"
                    )
                )


            elif (
                "citation" in issue_lower
                or
                "source" in issue_lower
            ):

                tasks.append(
                    ResearchTask(
                        query=issue,
                        reason="Find supporting evidence",
                        priority="high"
                    )
                )


            elif (
                "missing" in issue_lower
            ):

                tasks.append(
                    ResearchTask(
                        query=issue,
                        reason="Fill missing information",
                        priority="medium"
                    )
                )


        return tasks



class ResearchEngine:
    """
    Executes research.

    Can connect to:
    - Search APIs
    - Vector databases
    - Knowledge graph
    - Internal documents
    """



    def __init__(
        self,
        retriever=None
    ):

        self.retriever = retriever



    def execute(
        self,
        task: ResearchTask
    ) -> ResearchOutput:



        if self.retriever:


            results = (
                self.retriever.search(
                    task.query
                )
            )


            evidence = [
                Evidence(
                    content=item["content"],
                    source=item.get(
                        "source"
                    )
                )

                for item in results
            ]


            return ResearchOutput(
                query=task.query,
                evidence=evidence
            )


        return ResearchOutput(
            query=task.query,
            evidence=[
                Evidence(
                    content=
                    "No research backend configured"
                )
            ]
        )