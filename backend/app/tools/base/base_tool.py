from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseTool(ABC):

    name: str = ""
    description: str = ""
    version: str = "1.0.0"


    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        **kwargs: Any
    ):

        if name is not None:
            self.name = name

        if description is not None:
            self.description = description

        if version is not None:
            self.version = version


    @abstractmethod
    async def execute(
        self,
        **kwargs: Any
    ):
        pass