"""
Tests for knowledge_system.connectors package.

Verifies:
- package imports successfully
- all connector classes are exported
- connectors can be instantiated
"""

import pytest

from app.knowledge_system.connectors import (
    BaseConnector,
    ConnectorManager,
    APIConnector,
    ConfluenceConnector,
    DatabaseConnector,
    FileSystemConnector,
    GitHubConnector,
    GitLabConnector,
    JiraConnector,
    NotionConnector,
    SlackConnector,
    WebConnector,
)


def test_exports_exist():
    """All public exports should exist."""

    assert BaseConnector is not None
    assert ConnectorManager is not None

    assert APIConnector is not None
    assert ConfluenceConnector is not None
    assert DatabaseConnector is not None
    assert FileSystemConnector is not None
    assert GitHubConnector is not None
    assert GitLabConnector is not None
    assert JiraConnector is not None
    assert NotionConnector is not None
    assert SlackConnector is not None
    assert WebConnector is not None


@pytest.mark.parametrize(
    "connector_cls",
    [
        APIConnector,
        ConfluenceConnector,
        DatabaseConnector,
        FileSystemConnector,
        GitHubConnector,
        GitLabConnector,
        JiraConnector,
        NotionConnector,
        SlackConnector,
        WebConnector,
    ],
)
def test_connector_instantiation(connector_cls):
    """
    Every connector should be instantiable.

    If your connectors require constructor arguments,
    modify this test accordingly.
    """
    connector = connector_cls()

    assert connector is not None
    assert isinstance(connector, BaseConnector)


def test_connector_manager_instantiation():
    """ConnectorManager should instantiate."""

    manager = ConnectorManager()

    assert manager is not None