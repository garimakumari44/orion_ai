"""
Unit tests for the Knowledge Index Manager.
"""

from __future__ import annotations

from app.knowledge_system.indexing.manager import IndexManager


def test_index_manager_can_be_created():
    """IndexManager should instantiate successfully."""
    manager = IndexManager()

    assert isinstance(manager, IndexManager)


def test_index_returns_empty_list_for_empty_input():
    """Empty input should return an empty list."""
    manager = IndexManager()

    result = manager.index([])

    assert result == []


def test_index_returns_same_documents():
    """Documents should be returned unchanged."""
    manager = IndexManager()

    documents = [
        {
            "id": "doc1",
            "title": "Document One",
            "text": "Hello world",
        },
        {
            "id": "doc2",
            "title": "Document Two",
            "text": "Another document",
        },
    ]

    result = manager.index(documents)

    assert result == documents


def test_index_preserves_document_order():
    """Document ordering should remain unchanged."""
    manager = IndexManager()

    documents = [
        {"id": "1"},
        {"id": "2"},
        {"id": "3"},
    ]

    result = manager.index(documents)

    assert [doc["id"] for doc in result] == ["1", "2", "3"]


def test_index_returns_new_list():
    """The returned list should be a new list object."""
    manager = IndexManager()

    documents = [{"id": "doc1"}]

    result = manager.index(documents)

    assert result is not documents
    assert result == documents


def test_index_preserves_document_objects():
    """
    Current implementation is pass-through, so document objects
    themselves should not be copied.
    """
    manager = IndexManager()

    document = {"id": "doc1", "text": "hello"}

    result = manager.index([document])

    assert result[0] is document


def test_index_handles_documents_with_metadata():
    """Documents containing metadata should remain unchanged."""
    manager = IndexManager()

    documents = [
        {
            "id": "doc1",
            "metadata": {
                "source": "github",
                "author": "alice",
                "tags": ["python", "ai"],
            },
            "content": "Example",
        }
    ]

    result = manager.index(documents)

    assert result == documents
    assert result[0]["metadata"]["source"] == "github"
    assert result[0]["metadata"]["tags"] == ["python", "ai"]