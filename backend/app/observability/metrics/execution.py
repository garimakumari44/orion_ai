# metrics/execution.py

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional



@dataclass
class ExecutionMetric:
    """
    Stores execution workflow metrics.
    """

    execution_id: str

    workflow_name: str


    start_time: float = field(
        default_factory=time.time
    )


    end_time: Optional[float] = None


    total_tasks: int = 0

    completed_tasks: int = 0

    failed_tasks: int = 0


    retries: int = 0


    agents_used: List[str] = field(
        default_factory=list
    )


    error: Optional[str] = None



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



    @property
    def success_rate(self):

        if self.total_tasks == 0:
            return 0

        return (
            self.completed_tasks /
            self.total_tasks
        )



class ExecutionMetrics:
    """
    Tracks agent workflow executions.
    """

    def __init__(self):

        self.records: List[ExecutionMetric] = []



    def start(
        self,
        execution_id: str,
        workflow_name: str
    ):

        metric = ExecutionMetric(
            execution_id=execution_id,
            workflow_name=workflow_name
        )


        self.records.append(metric)

        return metric



    def record_progress(
        self,
        metric: ExecutionMetric,
        total_tasks: int,
        completed_tasks: int,
        failed_tasks: int = 0
    ):

        metric.total_tasks = total_tasks

        metric.completed_tasks = completed_tasks

        metric.failed_tasks = failed_tasks



    def add_agent(
        self,
        metric: ExecutionMetric,
        agent_name: str
    ):

        metric.agents_used.append(agent_name)



    def add_retry(
        self,
        metric: ExecutionMetric
    ):

        metric.retries += 1



    def finish(
        self,
        metric: ExecutionMetric
    ):

        metric.finish()



    def record_failure(
        self,
        metric: ExecutionMetric,
        error: Exception
    ):

        metric.error = str(error)

        metric.finish()



    def summary(self) -> Dict:


        total = len(self.records)


        if total == 0:
            return {}



        return {


            "total_executions":
                total,


            "avg_latency_ms":
                sum(
                    r.latency_ms
                    for r in self.records
                )
                /
                total,


            "avg_success_rate":
                sum(
                    r.success_rate
                    for r in self.records
                )
                /
                total,


            "total_failures":
                sum(
                    r.failed_tasks
                    for r in self.records
                ),


            "avg_retries":
                sum(
                    r.retries
                    for r in self.records
                )
                /
                total

        }



execution_metrics = ExecutionMetrics()