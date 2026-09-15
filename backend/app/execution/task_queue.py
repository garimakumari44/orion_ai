from __future__ import annotations

from collections import deque
from typing import Deque, Iterable, Optional

from app.planning.models.task_node import TaskNode


class TaskQueue:
    """
    FIFO queue for execution-ready tasks.

    The scheduler determines when tasks become ready.
    The execution engine uses this queue to dispatch work.
    """

    def __init__(self) -> None:
        self._queue: Deque[TaskNode] = deque()

    def enqueue(self, task: TaskNode) -> None:
        """
        Add a task to the end of the queue.
        """
        self._queue.append(task)

    def enqueue_many(self, tasks: Iterable[TaskNode]) -> None:
        """
        Add multiple tasks to the queue.
        """
        self._queue.extend(tasks)

    def dequeue(self) -> Optional[TaskNode]:
        """
        Remove and return the next task.

        Returns
        -------
        TaskNode | None
        """
        if not self._queue:
            return None

        return self._queue.popleft()

    def peek(self) -> Optional[TaskNode]:
        """
        Return the next task without removing it.
        """
        if not self._queue:
            return None

        return self._queue[0]

    def is_empty(self) -> bool:
        """
        Returns True if the queue has no tasks.
        """
        return len(self._queue) == 0

    def size(self) -> int:
        """
        Returns the number of queued tasks.
        """
        return len(self._queue)

    def clear(self) -> None:
        """
        Remove all queued tasks.
        """
        self._queue.clear()

    def __len__(self) -> int:
        return len(self._queue)

    def __iter__(self):
        return iter(self._queue)