"""
Load balancer for LLM providers.

Responsible for distributing requests across multiple provider
instances.

This module does NOT invoke providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from itertools import cycle
from threading import Lock
from typing import Dict, List


# ============================================================
# Provider Instance
# ============================================================

@dataclass(slots=True)
class ProviderInstance:
    """
    Represents one provider endpoint.
    """

    name: str
    endpoint: str
    weight: int = 1
    healthy: bool = True


# ============================================================
# Base Strategy
# ============================================================

class LoadBalancingStrategy(ABC):
    """
    Base interface for balancing strategies.
    """

    @abstractmethod
    def select(
        self,
        instances: List[ProviderInstance],
    ) -> ProviderInstance:
        pass


# ============================================================
# Round Robin
# ============================================================

class RoundRobinStrategy(LoadBalancingStrategy):

    def __init__(self) -> None:
        self._cycles: Dict[str, cycle] = {}
        self._lock = Lock()

    def select(
        self,
        instances: List[ProviderInstance],
    ) -> ProviderInstance:

        healthy = [i for i in instances if i.healthy]

        if not healthy:
            raise RuntimeError("No healthy provider instances.")

        key = "|".join(sorted(i.endpoint for i in healthy))

        with self._lock:

            if key not in self._cycles:
                self._cycles[key] = cycle(healthy)

            return next(self._cycles[key])


# ============================================================
# Least Requests
# ============================================================

class LeastRequestsStrategy(LoadBalancingStrategy):

    def __init__(self) -> None:
        self._requests = defaultdict(int)
        self._lock = Lock()

    def select(
        self,
        instances: List[ProviderInstance],
    ) -> ProviderInstance:

        healthy = [i for i in instances if i.healthy]

        if not healthy:
            raise RuntimeError("No healthy provider instances.")

        with self._lock:

            instance = min(
                healthy,
                key=lambda x: self._requests[x.endpoint],
            )

            self._requests[instance.endpoint] += 1

            return instance

    def release(
        self,
        instance: ProviderInstance,
    ) -> None:

        with self._lock:
            self._requests[instance.endpoint] = max(
                0,
                self._requests[instance.endpoint] - 1,
            )


# ============================================================
# Weighted Round Robin
# ============================================================

class WeightedRoundRobinStrategy(LoadBalancingStrategy):

    def __init__(self) -> None:
        self._cycles: Dict[str, cycle] = {}
        self._lock = Lock()

    def select(
        self,
        instances: List[ProviderInstance],
    ) -> ProviderInstance:

        healthy = [i for i in instances if i.healthy]

        if not healthy:
            raise RuntimeError("No healthy provider instances.")

        weighted = []

        for instance in healthy:
            weighted.extend([instance] * max(1, instance.weight))

        key = "|".join(
            sorted(f"{i.endpoint}:{i.weight}" for i in healthy)
        )

        with self._lock:

            if key not in self._cycles:
                self._cycles[key] = cycle(weighted)

            return next(self._cycles[key])


# ============================================================
# Load Balancer
# ============================================================

class LoadBalancer:
    """
    Coordinates provider selection.
    """

    def __init__(
        self,
        strategy: LoadBalancingStrategy,
    ) -> None:

        self.strategy = strategy

        self.instances: Dict[str, List[ProviderInstance]] = {}

    # --------------------------------------------------------

    def register(
        self,
        provider: str,
        instance: ProviderInstance,
    ) -> None:

        self.instances.setdefault(provider, []).append(instance)

    # --------------------------------------------------------

    def get_instance(
        self,
        provider: str,
    ) -> ProviderInstance:

        if provider not in self.instances:
            raise ValueError(
                f"No instances registered for '{provider}'."
            )

        return self.strategy.select(
            self.instances[provider]
        )

    # --------------------------------------------------------

    def mark_unhealthy(
        self,
        endpoint: str,
    ) -> None:

        for provider_instances in self.instances.values():
            for instance in provider_instances:
                if instance.endpoint == endpoint:
                    instance.healthy = False

    # --------------------------------------------------------

    def mark_healthy(
        self,
        endpoint: str,
    ) -> None:

        for provider_instances in self.instances.values():
            for instance in provider_instances:
                if instance.endpoint == endpoint:
                    instance.healthy = True

    # --------------------------------------------------------

    def all_instances(
        self,
    ) -> Dict[str, List[ProviderInstance]]:
        return self.instances