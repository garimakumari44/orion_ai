"""
Tracing middleware.

Integrates tracing system with FastAPI.

Responsibilities:

- Create root span per request
- Capture HTTP metadata
- Manage trace lifecycle
- Attach trace id to response headers
"""


import time
import traceback

from starlette.middleware.base import (
    BaseHTTPMiddleware
)

from starlette.requests import Request
from starlette.responses import Response


from .tracer import tracer
from .context import (
    set_trace_id,
    set_current_span,
    clear_context
)



class TracingMiddleware(
    BaseHTTPMiddleware
):

    """
    FastAPI tracing middleware.

    Example:

        app.add_middleware(
            TracingMiddleware
        )

    """


    async def dispatch(
        self,
        request: Request,
        call_next
    ):


        start_time = time.time()


        #
        # Create request trace
        #

        request_span = tracer.start_trace(
            "http_request"
        )


        set_trace_id(
            request_span.trace_id
        )


        set_current_span(
            request_span
        )


        #
        # Attach HTTP metadata
        #

        request_span.set_attribute(
            "http.method",
            request.method
        )


        request_span.set_attribute(
            "http.path",
            request.url.path
        )


        request_span.set_attribute(
            "http.client",
            request.client.host
            if request.client
            else None
        )


        try:

            response: Response = await call_next(
                request
            )


            #
            # Success metadata
            #

            request_span.set_attribute(
                "http.status_code",
                response.status_code
            )


            request_span.set_attribute(
                "http.duration_ms",
                (
                    time.time()
                    -
                    start_time
                )
                *
                1000
            )


            request_span.finish(
                status="success"
            )


            #
            # Add trace header
            #

            response.headers[
                "x-trace-id"
            ] = request_span.trace_id


            return response



        except Exception as error:


            #
            # Capture errors
            #

            request_span.set_attribute(
                "error.stack",
                traceback.format_exc()
            )


            request_span.fail(
                error
            )


            raise



        finally:


            #
            # Cleanup context
            #

            clear_context()