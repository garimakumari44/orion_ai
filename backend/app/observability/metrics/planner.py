# metrics/planner.py

import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict



@dataclass
class PlannerMetric:

    request_id: str

    start_time: float = field(
        default_factory=time.time
    )

    end_time: Optional[float] = None


    tasks_generated: int = 0

    tools_selected: List[str] = field(
        default_factory=list
    )

    replans: int = 0


    planning_strategy: str = "default"

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




class PlannerMetrics:


    def __init__(self):

        self.records = []



    def start(
        self,
        request_id: str,
        strategy="default"
    ):


        metric = PlannerMetric(
            request_id=request_id,
            planning_strategy=strategy
        )


        self.records.append(metric)


        return metric



    def record_plan(
        self,
        metric: PlannerMetric,
        tasks: int,
        tools: List[str]
    ):


        metric.tasks_generated = tasks

        metric.tools_selected = tools

        metric.finish()



    def record_replan(
        self,
        metric: PlannerMetric
    ):

        metric.replans += 1



    def record_failure(
        self,
        metric: PlannerMetric,
        error: Exception
    ):

        metric.error = str(error)

        metric.finish()



    def summary(self) -> Dict:


        total = len(self.records)


        if total == 0:
            return {}



        return {


            "total_plans":
                total,


            "avg_latency_ms":
                sum(
                    r.latency_ms
                    for r in self.records
                )
                /
                total,


            "avg_tasks":
                sum(
                    r.tasks_generated
                    for r in self.records
                )
                /
                total,


            "avg_replans":
                sum(
                    r.replans
                    for r in self.records
                )
                /
                total,


            "failed_plans":
                sum(
                    1
                    for r in self.records
                    if r.error
                )

        }



planner_metrics = PlannerMetrics()