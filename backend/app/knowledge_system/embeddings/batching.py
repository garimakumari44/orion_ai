"""
Utilities for batching embedding requests.
"""

from __future__ import annotations

from typing import Iterator, Sequence, TypeVar

T = TypeVar("T")


class BatchProcessor:
    """
    Splits sequences into fixed-size batches.
    """

    def __init__(
        self,
        batch_size: int = 32,
    ) -> None:
        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        self.batch_size = batch_size

    def split(
        self,
        items: Sequence[T],
    ) -> Iterator[list[T]]:
        """
        Yield batches of items.

        Example
        -------
        items = [1,2,3,4,5]
        batch_size = 2

        yields

        [1,2]
        [3,4]
        [5]
        """
        for start in range(
            0,
            len(items),
            self.batch_size,
        ):
            yield list(
                items[start : start + self.batch_size]
            )

    def __call__(
        self,
        items: Sequence[T],
    ) -> Iterator[list[T]]:
        return self.split(items)