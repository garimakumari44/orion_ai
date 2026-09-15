# metrics/cache.py

from dataclasses import dataclass, field
from typing import Dict



@dataclass
class CacheMetric:

    cache_name: str

    hits: int = 0

    misses: int = 0

    writes: int = 0

    metadata: Dict = field(
        default_factory=dict
    )


    @property
    def total_requests(self):

        return (
            self.hits +
            self.misses
        )


    @property
    def hit_rate(self):

        if self.total_requests == 0:
            return 0


        return round(
            self.hits /
            self.total_requests,
            4
        )



class CacheTracker:
    """
    Observability for caching systems.

    Tracks:
    - Redis cache
    - Vector cache
    - Prompt cache
    - Semantic cache
    """

    def __init__(self):

        self.caches = {}



    def register(
        self,
        name: str
    ):

        if name not in self.caches:

            self.caches[name] = CacheMetric(
                cache_name=name
            )



    def hit(
        self,
        name: str
    ):

        self.register(name)

        self.caches[name].hits += 1



    def miss(
        self,
        name: str
    ):

        self.register(name)

        self.caches[name].misses += 1



    def write(
        self,
        name: str
    ):

        self.register(name)

        self.caches[name].writes += 1



    def get_metrics(
        self
    ):

        return {

            name: {

                "hits":
                    cache.hits,

                "misses":
                    cache.misses,

                "writes":
                    cache.writes,

                "hit_rate":
                    cache.hit_rate
            }

            for name, cache
            in self.caches.items()
        }