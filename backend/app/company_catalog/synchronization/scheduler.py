import asyncio


class CompanySyncScheduler:


    def __init__(
        self,
        synchronizer,
        interval_hours: int = 24
    ):

        self.synchronizer = synchronizer

        self.interval_seconds = (
            interval_hours * 60 * 60
        )

        self.running = False



    async def start(self):

        self.running = True


        while self.running:


            try:

                await self.synchronizer.synchronize()


            except Exception as e:

                print(
                    "Company sync failed:",
                    e
                )


            await asyncio.sleep(
                self.interval_seconds
            )



    def stop(self):

        self.running = False