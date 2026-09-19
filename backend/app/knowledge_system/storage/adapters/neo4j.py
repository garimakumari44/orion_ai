"""
Neo4j Adapter

Graph database wrapper.
"""

from __future__ import annotations

from typing import Any

from neo4j import GraphDatabase


class Neo4jAdapter:

    def __init__(
        self,
        uri: str,
        username: str,
        password: str,
    ):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(username, password),
        )

    def close(self):

        self.driver.close()

    def run(
        self,
        query: str,
        **params,
    ):

        with self.driver.session() as session:
            return session.run(query, params)

    def execute_write(
        self,
        query: str,
        **params,
    ):

        with self.driver.session() as session:
            return session.execute_write(
                lambda tx: tx.run(query, params).consume()
            )

    def execute_read(
        self,
        query: str,
        **params,
    ):

        with self.driver.session() as session:
            result = session.execute_read(
                lambda tx: tx.run(query, params).data()
            )

        return result

    def health(self) -> bool:

        try:
            self.driver.verify_connectivity()
            return True
        except Exception:
            return False