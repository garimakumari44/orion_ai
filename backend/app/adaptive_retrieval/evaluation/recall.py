from typing import List, Set


class RecallEvaluator:
    """
    Measures how many relevant documents
    were successfully retrieved.
    """


    @staticmethod
    def recall(
        retrieved: List[str],
        relevant: Set[str]
    ) -> float:
        """
        Recall =
        Retrieved Relevant Documents /
        Total Relevant Documents
        """

        if not relevant:
            return 0.0


        retrieved_set = set(retrieved)

        true_positive = (
            retrieved_set & relevant
        )


        return (
            len(true_positive)
            /
            len(relevant)
        )



    @staticmethod
    def recall_at_k(
        ranked_results: List[str],
        relevant: Set[str],
        k: int
    ) -> float:
        """
        Recall@K

        Example:

        retrieved:
        [
          doc5,
          doc2,
          doc9
        ]

        k=2

        evaluates:
        [
          doc5,
          doc2
        ]
        """

        top_k = ranked_results[:k]

        return RecallEvaluator.recall(
            top_k,
            relevant
        )