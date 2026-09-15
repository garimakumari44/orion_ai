"""
Memory observability metrics.

Tracks:
- Memory reads
- Memory writes
- Retrieval latency
- Cache hits
- Retrieval scores
- Memory size
"""


import time
from dataclasses import dataclass
from typing import Dict


@dataclass
class MemoryMetric:

    name: str

    reads: int = 0
    writes: int = 0

    hits: int = 0
    misses: int = 0

    total_latency: float = 0.0

    retrieval_scores: list = None


    def __post_init__(self):

        if self.retrieval_scores is None:
            self.retrieval_scores = []



class MemoryMetrics:


    def __init__(self):

        self.memory: Dict[str, MemoryMetric] = {}



    def _get_memory(
        self,
        memory_name
    ):

        if memory_name not in self.memory:

            self.memory[memory_name] = (
                MemoryMetric(
                    name=memory_name
                )
            )

        return self.memory[memory_name]



    def record_read(
        self,
        memory_name: str,
        latency: float,
        hit: bool,
        score: float = None
    ):

        memory = self._get_memory(
            memory_name
        )


        memory.reads += 1


        memory.total_latency += latency


        if hit:
            memory.hits += 1

        else:
            memory.misses += 1



        if score is not None:

            memory.retrieval_scores.append(
                score
            )



    def record_write(
        self,
        memory_name: str
    ):

        memory = self._get_memory(
            memory_name
        )

        memory.writes += 1



    def get_metrics(self):

        result = {}


        for name, memory in self.memory.items():

            hit_rate = (

                memory.hits
                /
                memory.reads

                if memory.reads
                else 0

            )


            avg_latency = (

                memory.total_latency
                /
                memory.reads

                if memory.reads
                else 0

            )


            avg_score = (

                sum(memory.retrieval_scores)
                /
                len(memory.retrieval_scores)

                if memory.retrieval_scores
                else None

            )


            result[name] = {

                "reads":
                    memory.reads,

                "writes":
                    memory.writes,

                "hit_rate":
                    hit_rate,

                "miss_rate":
                    1-hit_rate,

                "avg_latency":
                    avg_latency,

                "avg_retrieval_score":
                    avg_score
            }


        return result