import asyncio
import functools
import random



def retry(
    retries:int = 3,
    delay:float = 1,
    backoff:float = 2
):


    def decorator(func):


        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            current_delay = delay


            for attempt in range(retries):

                try:

                    return await func(
                        *args,
                        **kwargs
                    )


                except Exception as e:


                    if attempt == retries - 1:
                        raise e


                    sleep_time = (
                        current_delay
                        +
                        random.random()
                    )


                    await asyncio.sleep(
                        sleep_time
                    )


                    current_delay *= backoff



        return wrapper


    return decorator