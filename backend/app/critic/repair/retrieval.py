"""
retrieval.py

Context recovery module.

Used when:
- Answer lacks evidence
- Missing information detected
- Hallucination suspected
- More context is required

Integrates with:
- Vector databases
- RAG systems
- Knowledge graph
- Document stores
"""


from dataclasses import dataclass
from typing import List, Optional, Any



@dataclass
class RetrievedContext:
    """
    Represents retrieved information.
    """

    content: str

    source: Optional[str] = None

    score: float = 0.0



class ContextRetriever:
    """
    Retrieves additional context
    for response repair.
    """


    def __init__(
        self,
        retriever: Any = None,
        top_k: int = 5
    ):

        self.retriever = retriever

        self.top_k = top_k



    def retrieve(
        self,
        query: str
    ) -> List[RetrievedContext]:
        """
        Retrieve relevant context.
        """


        if not self.retriever:

            return [
                RetrievedContext(
                    content=
                    "No retrieval backend configured."
                )
            ]



        results = (
            self.retriever.search(
                query=query,
                limit=self.top_k
            )
        )


        contexts = []


        for item in results:


            contexts.append(
                RetrievedContext(

                    content=item.get(
                        "content",
                        ""
                    ),

                    source=item.get(
                        "source"
                    ),

                    score=item.get(
                        "score",
                        0.0
                    )
                )
            )


        return contexts



    def build_context(
        self,
        contexts: List[RetrievedContext]
    ) -> str:
        """
        Convert retrieved chunks
        into LLM context.
        """

        output = []


        for context in contexts:

            output.append(
                f"""
Source:
{context.source}

Content:
{context.content}
"""
            )


        return "\n".join(output)