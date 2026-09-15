"""
Observability exporters.

Responsible for sending:
- traces
- metrics
- logs
- alerts
"""

import json
import requests
from pathlib import Path
from typing import Dict, Any



class BaseExporter:
    """
    Base exporter interface.
    """


    def export(
        self,
        data: Dict[str, Any]
    ):
        raise NotImplementedError



# --------------------------------------------------
# Console Exporter
# --------------------------------------------------

class ConsoleExporter(BaseExporter):
    """
    Prints telemetry data.
    """


    def export(
        self,
        data: Dict[str, Any]
    ):

        print(
            json.dumps(
                data,
                indent=4
            )
        )



# --------------------------------------------------
# JSON File Exporter
# --------------------------------------------------

class JSONExporter(BaseExporter):
    """
    Store telemetry in JSON file.
    """


    def __init__(
        self,
        file_path="observability.json"
    ):

        self.file_path = Path(
            file_path
        )



    def export(
        self,
        data: Dict[str, Any]
    ):

        records = []


        if self.file_path.exists():

            try:

                records = json.loads(
                    self.file_path.read_text()
                )

            except Exception:

                records = []


        records.append(data)


        self.file_path.write_text(
            json.dumps(
                records,
                indent=4,
                default=str
            )
        )



# --------------------------------------------------
# Webhook Exporter
# --------------------------------------------------

class WebhookExporter(BaseExporter):
    """
    Send telemetry to external service.
    """


    def __init__(
        self,
        url: str,
        timeout: int = 5
    ):

        self.url = url
        self.timeout = timeout



    def export(
        self,
        data: Dict[str, Any]
    ):

        try:

            response = requests.post(
                self.url,
                json=data,
                timeout=self.timeout
            )


            return {
                "status": response.status_code,
                "success": True
            }


        except Exception as error:

            return {
                "success": False,
                "error": str(error)
            }



# --------------------------------------------------
# Exporter Manager
# --------------------------------------------------

class ExporterManager:
    """
    Manage multiple exporters.
    """


    def __init__(self):

        self.exporters = []



    def register(
        self,
        exporter: BaseExporter
    ):

        self.exporters.append(
            exporter
        )



    def publish(
        self,
        data: Dict[str, Any]
    ):

        results = []


        for exporter in self.exporters:

            result = exporter.export(
                data
            )

            results.append(
                result
            )


        return results