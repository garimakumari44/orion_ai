from typing import Callable, List, Dict
import time



class BenchmarkRunner:
    """
    Benchmark complete AI pipelines.
    """

    def __init__(
        self,
        pipeline: Callable
    ):

        self.pipeline = pipeline



    def run(
        self,
        queries: List[str]
    ) -> Dict:


        results = []

        total_time = 0


        for query in queries:

            start = time.perf_counter()


            output = self.pipeline(
                query
            )


            latency = (
                time.perf_counter()
                -
                start
            )


            total_time += latency


            results.append(
                {
                    "query": query,
                    "latency_ms":
                        latency * 1000,
                    "success":
                        output is not None
                }
            )



        return {

            "total_queries":
                len(queries),

            "avg_latency_ms":
                (
                    total_time
                    /
                    len(queries)
                    *
                    1000
                ),

            "results":
                results
        }



    def compare(
        self,
        other_pipeline,
        queries
    ):

        first = self.run(
            queries
        )


        second = BenchmarkRunner(
            other_pipeline
        ).run(
            queries
        )


        return {

            "pipeline_a":
                first,

            "pipeline_b":
                second
        }