"""
Agent execution metrics.

Tracks:
- Agent calls
- Agent latency
- Agent failures
- Agent retries
- Agent confidence
- Agent token usage
- Agent success rate
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class AgentMetric:
    name: str

    calls: int = 0
    successes: int = 0
    failures: int = 0

    retries: int = 0

    total_latency: float = 0.0

    total_tokens: int = 0

    confidence_scores: list = field(default_factory=list)


class AgentMetrics:
    """
    Central registry for agent observability.
    """

    def __init__(self):

        self.agents: Dict[str, AgentMetric] = {}


    def _get_agent(
        self,
        agent_name: str
    ) -> AgentMetric:

        if agent_name not in self.agents:
            self.agents[agent_name] = AgentMetric(
                name=agent_name
            )

        return self.agents[agent_name]


    def start(
        self,
        agent_name: str
    ):
        """
        Start agent timer.
        """

        agent = self._get_agent(agent_name)

        agent.calls += 1

        return time.perf_counter()



    def record_success(
        self,
        agent_name: str,
        start_time: float,
        tokens: int = 0,
        confidence: Optional[float] = None
    ):

        agent = self._get_agent(agent_name)


        latency = (
            time.perf_counter()
            -
            start_time
        )


        agent.total_latency += latency

        agent.successes += 1

        agent.total_tokens += tokens


        if confidence is not None:
            agent.confidence_scores.append(
                confidence
            )



    def record_failure(
        self,
        agent_name: str,
        start_time: float,
    ):

        agent = self._get_agent(agent_name)

        latency = (
            time.perf_counter()
            -
            start_time
        )


        agent.total_latency += latency

        agent.failures += 1



    def record_retry(
        self,
        agent_name: str
    ):

        agent = self._get_agent(agent_name)

        agent.retries += 1



    def get_metrics(self):

        result = {}

        for name, agent in self.agents.items():

            total = (
                agent.successes
                +
                agent.failures
            )


            avg_latency = (
                agent.total_latency
                /
                agent.calls
                if agent.calls
                else 0
            )


            success_rate = (
                agent.successes
                /
                total
                if total
                else 0
            )


            avg_confidence = (
                sum(agent.confidence_scores)
                /
                len(agent.confidence_scores)
                if agent.confidence_scores
                else None
            )


            result[name] = {

                "calls": agent.calls,

                "success_rate":
                    success_rate,

                "failure_rate":
                    1 - success_rate
                    if total
                    else 0,

                "avg_latency":
                    avg_latency,

                "retries":
                    agent.retries,

                "tokens":
                    agent.total_tokens,

                "avg_confidence":
                    avg_confidence
            }


        return result