# metrics/tools.py

import time

from dataclasses import dataclass, field

from typing import Dict, Optional, List



@dataclass
class ToolMetric:


    tool_name: str


    start_time: float = field(
        default_factory=time.time
    )


    end_time: Optional[float] = None


    success: bool = False


    retries: int = 0


    error: Optional[str] = None


    metadata: Dict = field(
        default_factory=dict
    )



    def finish(self):

        self.end_time = time.time()



    @property
    def latency_ms(self):

        if not self.end_time:
            return 0


        return (
            self.end_time -
            self.start_time
        ) * 1000




class ToolMetrics:


    def __init__(self):

        self.records: List[ToolMetric] = []



    def start(
        self,
        tool_name: str,
        metadata=None
    ):


        metric = ToolMetric(
            tool_name=tool_name,
            metadata=metadata or {}
        )


        self.records.append(metric)

        return metric




    def record_success(
        self,
        metric: ToolMetric
    ):

        metric.success = True

        metric.finish()




    def record_failure(
        self,
        metric: ToolMetric,
        error: Exception
    ):

        metric.error = str(error)

        metric.success = False

        metric.finish()




    def add_retry(
        self,
        metric: ToolMetric
    ):

        metric.retries += 1




    def summary(self):


        total = len(self.records)


        if total == 0:
            return {}



        successful = [
            r for r in self.records
            if r.success
        ]



        return {


            "total_tool_calls":
                total,


            "success_rate":
                len(successful)
                /
                total,


            "avg_latency_ms":
                sum(
                    r.latency_ms
                    for r in self.records
                )
                /
                total,


            "failed_calls":
                total -
                len(successful)

        }



tool_metrics = ToolMetrics()