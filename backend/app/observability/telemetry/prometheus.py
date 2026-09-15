"""
Prometheus metrics integration.

Provides:
- Counters
- Histograms
- Gauges
- Metrics registry
"""


from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    generate_latest
)



class PrometheusManager:


    def __init__(self):

        self.registry = CollectorRegistry()


        # Requests

        self.requests_total = Counter(
            "ai_requests_total",
            "Total AI requests",
            registry=self.registry
        )


        self.request_latency = Histogram(
            "ai_request_latency_seconds",
            "AI request latency",
            registry=self.registry
        )



        # LLM metrics

        self.tokens_used = Counter(
            "ai_tokens_total",
            "Total tokens consumed",
            [
                "model"
            ],
            registry=self.registry
        )



        self.llm_cost = Counter(
            "ai_cost_total",
            "Total LLM cost",
            registry=self.registry
        )



        # Agent metrics


        self.agent_calls = Counter(
            "agent_calls_total",
            "Agent executions",
            [
                "agent"
            ],
            registry=self.registry
        )


        self.agent_failures = Counter(
            "agent_failures_total",
            "Agent failures",
            [
                "agent"
            ],
            registry=self.registry
        )



        # Memory


        self.memory_hits = Counter(
            "memory_hits_total",
            "Memory cache hits",
            [
                "memory"
            ],
            registry=self.registry
        )


        self.memory_latency = Histogram(
            "memory_latency_seconds",
            "Memory retrieval latency",
            [
                "memory"
            ],
            registry=self.registry
        )



        # System health


        self.active_agents = Gauge(
            "active_agents",
            "Currently running agents",
            registry=self.registry
        )



    def record_request(self):

        self.requests_total.inc()



    def record_latency(
        self,
        seconds: float
    ):

        self.request_latency.observe(
            seconds
        )



    def record_tokens(
        self,
        model: str,
        tokens: int
    ):

        self.tokens_used.labels(
            model=model
        ).inc(
            tokens
        )



    def record_agent_call(
        self,
        agent: str
    ):

        self.agent_calls.labels(
            agent=agent
        ).inc()



    def record_agent_failure(
        self,
        agent: str
    ):

        self.agent_failures.labels(
            agent=agent
        ).inc()



    def metrics_output(self):

        return generate_latest(
            self.registry
        )



prometheus = PrometheusManager()