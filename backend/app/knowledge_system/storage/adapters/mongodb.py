"""
MongoDB Adapter

Responsibilities
----------------
- Document storage
- Flexible metadata
- Collections
- CRUD operations
"""

from __future__ import annotations

from typing import Any

from pymongo import MongoClient


class MongoDBAdapter:
    """
    Thin MongoDB wrapper.
    """

    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        database: str = "knowledge_system",
    ):
        self.client = MongoClient(uri)
        self.db = self.client[database]

    def collection(
        self,
        name: str,
    ):
        return self.db[name]

    def insert_one(
        self,
        collection: str,
        document: dict,
    ):
        return self.db[collection].insert_one(document)

    def insert_many(
        self,
        collection: str,
        documents: list[dict],
    ):
        return self.db[collection].insert_many(documents)

    def find_one(
        self,
        collection: str,
        query: dict,
    ):
        return self.db[collection].find_one(query)

    def find(
        self,
        collection: str,
        query: dict,
    ):
        return self.db[collection].find(query)

    def update_one(
        self,
        collection: str,
        query: dict,
        update: dict,
    ):
        return self.db[collection].update_one(
            query,
            update,
        )

    def delete_one(
        self,
        collection: str,
        query: dict,
    ):
        return self.db[collection].delete_one(query)

    def health(self) -> bool:
        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            return False