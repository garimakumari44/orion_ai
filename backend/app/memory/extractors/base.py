"""
Base Memory Extractor

All extractors convert raw data into structured Memory objects.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.memory.models.memory import Memory


class BaseExtractor(ABC):
    """
    Base class for every memory extractor.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def extract(self, data: Any) -> List[Memory]:
        """
        Extract memories from input.

        Parameters
        ----------
        data:
            Raw input.

        Returns
        -------
        List[Memory]
        """
        raise NotImplementedError

    def metadata(self) -> Dict[str, Any]:
        """
        Metadata describing this extractor.
        """

        return {
            "name": self.name,
            "type": self.__class__.__name__,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"