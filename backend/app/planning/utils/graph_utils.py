"""
Generic graph utilities.

These functions are independent of the planner and can be
reused anywhere that works with Directed Acyclic Graphs (DAGs).
"""

from collections import deque
from typing import Dict, List, Set


def topological_sort(
    graph: Dict[str, List[str]],
    in_degree: Dict[str, int],
) -> List[str]:
    """
    Performs Kahn's Topological Sort.

    Args:
        graph:
            parent -> children adjacency list

        in_degree:
            node -> incoming edge count

    Returns:
        Ordered list of nodes.

    Raises:
        ValueError if graph contains a cycle.
    """

    queue = deque()

    for node, degree in in_degree.items():
        if degree == 0:
            queue.append(node)

    ordering = []

    current_degree = dict(in_degree)

    while queue:
        node = queue.popleft()
        ordering.append(node)

        for child in graph.get(node, []):

            current_degree[child] -= 1

            if current_degree[child] == 0:
                queue.append(child)

    if len(ordering) != len(in_degree):
        raise ValueError("Cycle detected during topological sort.")

    return ordering


def reverse_graph(
    graph: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    Builds reverse adjacency list.

    parent -> children

    becomes

    child -> parents
    """

    reverse = {node: [] for node in graph}

    for parent, children in graph.items():

        for child in children:

            reverse.setdefault(child, []).append(parent)

    return reverse


def find_roots(
    in_degree: Dict[str, int]
) -> List[str]:
    """
    Returns nodes with zero dependencies.
    """

    return [
        node
        for node, degree in in_degree.items()
        if degree == 0
    ]


def find_leaves(
    graph: Dict[str, List[str]]
) -> List[str]:
    """
    Returns nodes with no outgoing edges.
    """

    return [
        node
        for node, children in graph.items()
        if len(children) == 0
    ]


def reachable_nodes(
    graph: Dict[str, List[str]],
    start: str,
) -> Set[str]:
    """
    Returns every node reachable from start.
    """

    visited = set()

    stack = [start]

    while stack:

        node = stack.pop()

        if node in visited:
            continue

        visited.add(node)

        stack.extend(graph.get(node, []))

    return visited