"""
Tracing decorators.

Provides automatic span creation
for functions and async functions.
"""


import functools
import asyncio

from .tracer import tracer



def trace(
    name: str = None,
    attributes: dict = None
):
    """
    Decorator for tracing functions.

    Usage:

    @trace(
        "embedding_generation"
    )
    def create_embedding():
        pass

    """


    def decorator(func):

        span_name = (
            name
            or func.__name__
        )


        # Async function support

        if asyncio.iscoroutinefunction(
            func
        ):


            @functools.wraps(func)
            async def async_wrapper(
                *args,
                **kwargs
            ):


                span = tracer.start_span(
                    span_name,
                    attributes
                )


                try:

                    result = await func(
                        *args,
                        **kwargs
                    )


                    tracer.end_span(
                        span
                    )


                    return result


                except Exception as e:

                    span.fail(e)

                    raise



            return async_wrapper



        # Normal function support


        @functools.wraps(func)
        def wrapper(
            *args,
            **kwargs
        ):


            span = tracer.start_span(
                span_name,
                attributes
            )


            try:

                result = func(
                    *args,
                    **kwargs
                )


                tracer.end_span(
                    span
                )


                return result


            except Exception as e:

                span.fail(e)

                raise



        return wrapper


    return decorator