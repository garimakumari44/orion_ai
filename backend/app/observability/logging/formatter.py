"""
formatter.py

Structured JSON log formatter.
"""


import json
import logging
from datetime import datetime, timezone



class JSONFormatter(
    logging.Formatter
):
    """
    Formats logs as JSON objects.
    """


    def format(
        self,
        record: logging.LogRecord
    ):

        log_record = {

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),


            "level":
                record.levelname,


            "logger":
                record.name,


            "message":
                record.getMessage(),

        }



        #
        # Include structured metadata
        #

        excluded = {

            "name",
            "msg",
            "args",
            "created",
            "msecs",
            "relativeCreated",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "lineno",
            "funcName",
            "exc_info",
            "exc_text",
            "stack_info",
        }



        extra_fields = {

            key:value

            for key,value in record.__dict__.items()

            if key not in excluded

        }


        if extra_fields:

            log_record.update(
                extra_fields
            )


        #
        # Exception handling
        #

        if record.exc_info:

            log_record["exception"] = (
                self.formatException(
                    record.exc_info
                )
            )


        return json.dumps(
            log_record,
            ensure_ascii=False
        )