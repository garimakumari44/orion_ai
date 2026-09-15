from typing import List, Set, Dict


class RetrievalMetrics:
    """
    Collection of retrieval evaluation metrics.
    """


    @staticmethod
    def hit_rate(
        retrieved: List[str],
        relevant: Set[str]
    ) -> float:
        """
        Measures whether at least one relevant item was retrieved.

        Hit Rate =
            1 if intersection exists else 0
        """

        if not retrieved:
            return 0.0

        return 1.0 if set(retrieved) & relevant else 0.0


    @staticmethod
    def f1_score(
        precision: float,
        recall: float
    ) -> float:
        """
        Harmonic mean of precision and recall.
        """

        if precision + recall == 0:
            return 0.0

        return (
            2 * precision * recall /
            (precision + recall)
        )


    @staticmethod
    def mean_average_precision(
        results: List[List[str]],
        relevant_sets: List[Set[str]]
    ) -> float:
        """
        MAP evaluation over multiple queries.

        results:
            [
                ["doc1","doc2"],
                ["doc3","doc4"]
            ]

        relevant_sets:
            [
                {"doc1"},
                {"doc4"}
            ]
        """

        if not results:
            return 0.0


        scores = []

        for retrieved, relevant in zip(
            results,
            relevant_sets
        ):

            hits = 0
            precision_sum = 0


            for idx, doc in enumerate(retrieved, start=1):

                if doc in relevant:
                    hits += 1

                    precision_sum += (
                        hits / idx
                    )


            if relevant:
                scores.append(
                    precision_sum / len(relevant)
                )


        return (
            sum(scores) / len(scores)
            if scores
            else 0.0
        )


    @staticmethod
    def reciprocal_rank(
        retrieved: List[str],
        relevant: Set[str]
    ) -> float:
        """
        Mean Reciprocal Rank helper.

        Returns position of first relevant result.
        """

        for idx, doc in enumerate(
            retrieved,
            start=1
        ):
            if doc in relevant:
                return 1 / idx

        return 0.0