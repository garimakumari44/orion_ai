"""
heartbeat.py

Service heartbeat tracking.

Used for:
- Agent workers
- Background jobs
- Distributed services
- Event consumers
"""


import time
import threading
from datetime import datetime, timezone
from typing import Dict, Any



class Heartbeat:

    """
    Represents heartbeat of a service.
    """

    def __init__(
        self,
        service_name: str
    ):

        self.service_name = service_name

        self.last_seen = datetime.now(
            timezone.utc
        )

        self.counter = 0



    def beat(self):
        """
        Update heartbeat timestamp.
        """

        self.last_seen = datetime.now(
            timezone.utc
        )

        self.counter += 1



    def age_seconds(self):

        return (
            datetime.now(
                timezone.utc
            )
            -
            self.last_seen
        ).total_seconds()



    def healthy(
        self,
        timeout: int = 30
    ):

        return (
            self.age_seconds()
            < timeout
        )



    def to_dict(self):

        return {

            "service":
                self.service_name,

            "last_seen":
                self.last_seen.isoformat(),

            "beats":
                self.counter,

            "healthy":
                self.healthy()
        }



class HeartbeatManager:
    """
    Tracks multiple service heartbeats.

    Example:

    LLM Worker
    Retriever Worker
    Planner Worker
    Tool Executor
    """

    def __init__(self):

        self.services: Dict[
            str,
            Heartbeat
        ] = {}



    def register(
        self,
        service_name: str
    ):

        self.services[
            service_name
        ] = Heartbeat(
            service_name
        )



    def beat(
        self,
        service_name: str
    ):

        if service_name not in self.services:
            self.register(service_name)


        self.services[
            service_name
        ].beat()



    def check(
        self
    ) -> Dict[str, Any]:

        return {

            name:
                heartbeat.to_dict()

            for name, heartbeat
            in self.services.items()

        }



    def failed_services(
        self,
        timeout=30
    ):

        return [

            name

            for name, heartbeat
            in self.services.items()

            if not heartbeat.healthy(timeout)

        ]



class HeartbeatRunner:
    """
    Background heartbeat sender.
    """

    def __init__(
        self,
        manager: HeartbeatManager,
        service_name: str,
        interval: int = 10
    ):

        self.manager = manager
        self.service_name = service_name
        self.interval = interval

        self.running = False
        self.thread = None



    def start(self):

        self.running = True

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self.thread.start()



    def stop(self):

        self.running = False



    def _run(self):

        while self.running:

            self.manager.beat(
                self.service_name
            )

            time.sleep(
                self.interval
            )