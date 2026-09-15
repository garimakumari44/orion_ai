"""
Telemetry exporters.

Responsible for sending observability data
to external monitoring systems.

Supported:
- OTLP
- JSON
- Custom exporters
"""


import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any



class BaseExporter(ABC):
    """
    Base exporter interface.
    """


    @abstractmethod
    def export(
        self,
        data: Dict[str, Any]
    ):
        pass




class JSONExporter(BaseExporter):
    """
    Writes telemetry events as JSON.

    Useful for:
    - debugging
    - local development
    - log pipelines
    """


    def __init__(
        self,
        file_path="telemetry.json"
    ):

        self.file_path = file_path



    def export(
        self,
        data
    ):

        payload = {

            "timestamp":
                time.time(),

            "data":
                data
        }


        with open(
            self.file_path,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                json.dumps(payload)
                +
                "\n"
            )





class OTLPExporter(BaseExporter):
    """
    OpenTelemetry Protocol exporter.

    Sends telemetry to:
    - Jaeger
    - Grafana Tempo
    - OpenTelemetry Collector
    """


    def __init__(
        self,
        endpoint: str
    ):

        self.endpoint = endpoint



    def export(
        self,
        data
    ):

        # Placeholder

        # Real implementation:
        # requests.post(
        #     self.endpoint,
        #     json=data
        # )

        print(
            f"Sending telemetry to {self.endpoint}"
        )





class PrometheusExporter(BaseExporter):
    """
    Prometheus exporter.

    Prometheus usually pulls metrics,
    so this exporter prepares metrics
    for scraping.
    """


    def __init__(
        self,
        registry
    ):

        self.registry = registry



    def export(
        self,
        data
    ):

        return data






class ExporterManager:
    """
    Manages multiple exporters.
    """


    def __init__(self):

        self.exporters = []



    def add(
        self,
        exporter: BaseExporter
    ):

        self.exporters.append(
            exporter
        )



    def publish(
        self,
        data
    ):

        for exporter in self.exporters:

            try:

                exporter.export(
                    data
                )


            except Exception as error:

                print(
                    "Exporter failed:",
                    error
                )




exporter_manager = ExporterManager()