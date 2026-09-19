"""
Storage interface for knowledge graphs.

Supported implementations:
- Neo4j
- Memgraph
- ArangoDB
- NetworkX (testing)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class GraphStore(ABC):
    """Abstract graph storage interface."""


    @abstractmethod
    async def add_node(
        self,
        node_id: str,
        label: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        ...


    @abstractmethod
    async def get_node(
        self,
        node_id: str,
    ) -> Optional[Dict[str, Any]]:
        ...


    @abstractmethod
    async def delete_node(
        self,
        node_id: str,
    ) -> None:
        ...


    @abstractmethod
    async def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        ...


    @abstractmethod
    async def get_neighbors(
        self,
        node_id: str,
        relation: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        ...


    @abstractmethod
    async def remove_edge(
        self,
        source: str,
        target: str,
        relation: str,
    ) -> None:
        ...



class InMemoryGraphStore(GraphStore):
    """
    Simple graph implementation.

    Intended for testing.
    """


    def __init__(self):

        self.nodes: Dict[
            str,
            Dict[str, Any]
        ] = {}

        self.edges: List[
            Dict[str, Any]
        ] = {}



    async def initialize(self):
        """
        Initialize graph storage.
        """

        self.nodes = {}

        self.edges = []



    async def close(self):
        """
        Cleanup graph storage.
        """

        self.nodes.clear()

        self.edges.clear()



    async def add_node(
        self,
        node_id: str,
        label: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:

        self.nodes[node_id] = {

            "id": node_id,

            "label": label,

            "properties": properties or {},
        }



    async def get_node(
        self,
        node_id: str,
    ) -> Optional[Dict[str, Any]]:

        return self.nodes.get(node_id)



    async def delete_node(
        self,
        node_id: str,
    ) -> None:

        self.nodes.pop(
            node_id,
            None,
        )

        self.edges = [
            edge
            for edge in self.edges
            if edge["source"] != node_id
            and edge["target"] != node_id
        ]



    async def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:

        self.edges.append(
            {
                "source": source,
                "target": target,
                "relation": relation,
                "properties": properties or {},
            }
        )



    async def get_neighbors(
        self,
        node_id: str,
        relation: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        neighbors = []


        for edge in self.edges:

            if edge["source"] != node_id:
                continue


            if relation and edge["relation"] != relation:
                continue


            node = self.nodes.get(
                edge["target"]
            )


            if node:

                neighbors.append(
                    {
                        "relation": edge["relation"],
                        "node": node,
                    }
                )


        return neighbors



    async def remove_edge(
        self,
        source: str,
        target: str,
        relation: str,
    ) -> None:

        self.edges = [
            edge
            for edge in self.edges
            if not (
                edge["source"] == source
                and edge["target"] == target
                and edge["relation"] == relation
            )
        ]