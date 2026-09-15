# metrics/retrieval.py

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RetrievalMetric:
    """
    Stores retrieval performance metrics.
    """

    query: str

    retriever_type: str

    start_time: float = field(default_factory=time.time)

    end_time: Optional[float] = None

    documents_retrieved: int = 0

    top_k: int = 0

    scores: List[float] = field(default_factory=list)

    cache_hit: bool = False

    error: Optional[str] = None


    def finish(self):
        self.end_time = time.time()


    @property
    def latency_ms(self) -> float:
        if not self.end_time:
            return 0.0

        return (self.end_time - self.start_time) * 1000


    @property
    def average_score(self) -> float:
        if not self.scores:
            return 0.0

        return sum(self.scores) / len(self.scores)



class RetrievalMetrics:
    """
    Global retrieval metrics collector.
    """

    def __init__(self):

        self.records: List[RetrievalMetric] = []


    def start(
        self,
        query: str,
        retriever_type: str,
        top_k: int = 5
    ) -> RetrievalMetric:

        metric = RetrievalMetric(
            query=query,
            retriever_type=retriever_type,
            top_k=top_k
        )

        self.records.append(metric)

        return metric



    def record_success(
        self,
        metric: RetrievalMetric,
        documents_count: int,
        scores: List[float],
        cache_hit: bool = False
    ):

        metric.documents_retrieved = documents_count
        metric.scores = scores
        metric.cache_hit = cache_hit

        metric.finish()



    def record_failure(
        self,
        metric: RetrievalMetric,
        error: Exception
    ):

        metric.error = str(error)

        metric.finish()



    def summary(self) -> Dict:

        total = len(self.records)

        if total == 0:
            return {}


        successful = [
            r for r in self.records
            if r.error is None
        ]


        return {

            "total_queries": total,

            "successful_queries": len(successful),

            "failed_queries": total - len(successful),

            "avg_latency_ms":
                sum(
                    r.latency_ms
                    for r in self.records
                ) / total,

            "avg_documents":
                sum(
                    r.documents_retrieved
                    for r in self.records
                ) / total,

            "cache_hit_rate":
                sum(
                    1 for r in self.records
                    if r.cache_hit
                ) / total,

            "avg_relevance_score":
                sum(
                    r.average_score
                    for r in successful
                ) / max(len(successful),1)
        }



retrieval_metrics = RetrievalMetrics()