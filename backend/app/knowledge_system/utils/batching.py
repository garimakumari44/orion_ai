"""
Utilities for batching collections.

Used throughout the knowledge system for:
- Embedding generation
- Vector database upserts
- LLM requests
- Database inserts
- Bulk indexing
"""

from __future__ import annotations

from itertools import islice
from math import ceil
from typing import Iterable, Iterator, Sequence, TypeVar

T = TypeVar("T")


def batch_iterable(
    iterable: Iterable[T],
    batch_size: int,
) -> Iterator[list[T]]:
    """
    Lazily yield batches from any iterable.

    Example:
        >>> list(batch_iterable(range(10), 3))
        [[0,1,2],[3,4,5],[6,7,8],[9]]
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    iterator = iter(iterable)

    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            break
        yield batch


def batch_sequence(
    sequence: Sequence[T],
    batch_size: int,
) -> Iterator[Sequence[T]]:
    """
    Batch an indexable sequence using slicing.
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    for i in range(0, len(sequence), batch_size):
        yield sequence[i : i + batch_size]


def split_batches(
    sequence: Sequence[T],
    batch_size: int,
) -> list[list[T]]:
    """
    Return all batches as a list.
    """

    return [
        list(batch)
        for batch in batch_sequence(sequence, batch_size)
    ]


def num_batches(
    total_items: int,
    batch_size: int,
) -> int:
    """
    Number of batches required.
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    return ceil(total_items / batch_size)


def flatten(
    batches: Iterable[Iterable[T]],
) -> list[T]:
    """
    Flatten nested batches.
    """

    return [
        item
        for batch in batches
        for item in batch
    ]