"""
Telemetry collectors.

Collects metrics from internal
AI platform components.

Sources:
- Agents
- Memory
- LLM
- Retrieval
- Tools
"""


import time
from typing import Dict, Any



class BaseCollector:
    """
    Collector interface.
    """


    def collect(self):
        raise NotImplementedError





class AgentCollector(BaseCollector):


    def __init__(
        self,
        agent_metrics
    ):

        self.agent_metrics = agent_metrics



    def collect(self):

        return {

            "agents":
                self.agent_metrics.get_metrics()

        }





class MemoryCollector(BaseCollector):


    def __init__(
        self,
        memory_metrics
    ):

        self.memory_metrics = memory_metrics



    def collect(self):

        return {

            "memory":
                self.memory_metrics.get_metrics()

        }





class RuntimeCollector(BaseCollector):
    """
    System runtime metrics.
    """


    def collect(self):

        return {

            "runtime": {

                "timestamp":
                    time.time()

            }

        }





class CollectorManager:
    """
    Runs all collectors.
    """


    def __init__(self):

        self.collectors = []



    def add(
        self,
        collector: BaseCollector
    ):

        self.collectors.append(
            collector
        )



    def collect_all(self):

        result = {}


        for collector in self.collectors:

            try:

                data = collector.collect()

                result.update(
                    data
                )


            except Exception as error:

                result[
                    "collector_error"
                ] = str(error)



        return result





collector_manager = CollectorManager()