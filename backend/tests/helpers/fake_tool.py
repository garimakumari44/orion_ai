from app.tools.base_tool import BaseTool
from app.orchestration.capability import Capability


class FakeTool(BaseTool):

    def __init__(
        self,
        name="fake_tool",
        priority=1,
        enabled=True,
        healthy=True,
        capabilities=None,
        should_fail=False,
        fail_times=0,
    ):

        self.name = name
        self.priority = priority
        self.enabled = enabled
        self.healthy = healthy

        self.capabilities = capabilities or [
            Capability.WEB_SEARCH
        ]

        self.should_fail = should_fail
        self.fail_times = fail_times
        self.execution_count = 0


    # -------------------------------------------------
    # Capability check
    # -------------------------------------------------

    def supports(
        self,
        capability: Capability,
    ) -> bool:

        return capability in self.capabilities


    # -------------------------------------------------
    # Availability check
    # -------------------------------------------------

    def is_available(self) -> bool:

        return (
            self.enabled
            and self.healthy
        )


    # -------------------------------------------------
    # Execution
    # -------------------------------------------------

    async def execute(
        self,
        **kwargs,
    ):

        self.execution_count += 1


        if self.should_fail:

            raise Exception(
                "Tool failed"
            )


        if self.execution_count <= self.fail_times:

            raise RuntimeError(
                "Temporary failure"
            )


        return {
            "message": "success"
        }