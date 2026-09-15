from typing import List, Set


class PrecisionEvaluator:
    """
    Measures retrieval accuracy.
    """


    @staticmethod
    def precision(
        retrieved: List[str],
        relevant: Set[str]
    ) -> float:
        """
        Precision =
        Relevant Retrieved /
        Total Retrieved
        """

        if not retrieved:
            return 0.0


        retrieved_set = set(retrieved)

        correct = (
            retrieved_set & relevant
        )


        return (
            len(correct)
            /
            len(retrieved_set)
        )



    @staticmethod
    def precision_at_k(
        ranked_results: List[str],
        relevant: Set[str],
        k: int
    ) -> float:
        """
        Precision@K
        """

        top_k = ranked_results[:k]


        if not top_k:
            return 0.0


        correct = [
            doc
            for doc in top_k
            if doc in relevant
        ]


        return (
            len(correct)
            /
            k
        )



    @staticmethod
    def average_precision(
        ranked_results: List[str],
        relevant: Set[str]
    ) -> float:

        score = 0.0
        hits = 0


        for idx, doc in enumerate(
            ranked_results,
            start=1
        ):

            if doc in relevant:

                hits += 1

                score += (
                    hits / idx
                )


        if not relevant:
            return 0.0


        return score / len(relevant)