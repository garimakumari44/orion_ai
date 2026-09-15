"""
Dependency helper functions.

Used for validating and manipulating planner task
dependencies before graph construction.
"""

from typing import Dict, List, Set

from app.planning.models.task import Task


def dependency_map(
    tasks: List[Task]
) -> Dict[str, List[str]]:
    """
    Converts task list into

    task_id -> dependency ids
    """

    return {
        task.id: list(task.dependencies)
        for task in tasks
    }


def validate_dependencies(
    tasks: List[Task]
) -> None:
    """
    Ensures every dependency refers
    to an existing task.
    """

    task_ids = {
        task.id
        for task in tasks
    }

    for task in tasks:

        for dep in task.dependencies:

            if dep not in task_ids:
                raise ValueError(
                    f"Task '{task.id}' depends on "
                    f"unknown task '{dep}'."
                )


def duplicate_dependencies(
    task: Task
) -> Set[str]:
    """
    Returns duplicate dependency IDs.
    """

    seen = set()
    duplicates = set()

    for dep in task.dependencies:

        if dep in seen:
            duplicates.add(dep)

        seen.add(dep)

    return duplicates


def remove_duplicate_dependencies(
    task: Task
) -> None:
    """
    Removes duplicated dependencies while
    preserving order.
    """

    unique = []

    seen = set()

    for dep in task.dependencies:

        if dep not in seen:
            unique.append(dep)
            seen.add(dep)

    task.dependencies = unique


def validate_no_self_dependency(
    task: Task
) -> None:
    """
    Prevents task depending on itself.
    """

    if task.id in task.dependencies:
        raise ValueError(
            f"Task '{task.id}' cannot depend on itself."
        )


def validate_all_tasks(
    tasks: List[Task]
) -> None:
    """
    Runs all dependency validation checks.
    """

    validate_dependencies(tasks)

    for task in tasks:

        validate_no_self_dependency(task)

        duplicates = duplicate_dependencies(task)

        if duplicates:
            raise ValueError(
                f"Task '{task.id}' has duplicate dependencies: "
                f"{sorted(duplicates)}"
            )