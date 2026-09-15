"""
tests/agents/unit/test_github_agent.py

Unit tests for GitHubAgent.
"""

import pytest

from app.agents.github.github_agent import GitHubAgent
from app.agents.base.agent_context import AgentContext


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def agent():
    return GitHubAgent()


def make_context(
    capability: str,
    query: str = "test query",
    task: str | None = None,
    **metadata,
):
    ctx = AgentContext(
        query=query,
        task=task,
    )

    # GitHubAgent expects context.metadata
    ctx.metadata = {
        "capability": capability,
        **metadata,
    }

    return ctx


# ---------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------

def test_agent_initialization(agent):
    assert agent.name == "github"

    assert "GitHub" in agent.description

    assert agent.supports("repository_search")
    assert agent.supports("repository_analysis")
    assert agent.supports("repository_metadata")
    assert agent.supports("issue_search")
    assert agent.supports("issue_analysis")
    assert agent.supports("pull_request_review")
    assert agent.supports("pull_request_search")
    assert agent.supports("commit_history")
    assert agent.supports("release_information")
    assert agent.supports("branch_information")
    assert agent.supports("code_search")
    assert agent.supports("contributor_analysis")
    assert agent.supports("repository_statistics")

    assert not agent.supports("weather")


# ---------------------------------------------------------------------
# Repository Search
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_repository_search(agent):
    ctx = make_context(
        "repository_search",
        task="Find FastAPI repositories",
    )

    result = await agent.execute(ctx)

    assert result["success"] is True
    assert result["operation"] == "repository_search"
    assert result["query"] == "Find FastAPI repositories"
    assert result["status"] == "pending_tool_execution"


# ---------------------------------------------------------------------
# Repository Analysis
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_repository_analysis(agent):
    ctx = make_context(
        "repository_analysis",
        repository="openai/openai-python",
    )

    result = await agent.execute(ctx)

    assert result["success"] is True
    assert result["operation"] == "repository_analysis"
    assert result["repository"] == "openai/openai-python"


# ---------------------------------------------------------------------
# Repository Metadata
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_repository_metadata(agent):
    ctx = make_context(
        "repository_metadata",
        repository="psf/requests",
    )

    result = await agent.execute(ctx)

    assert result["operation"] == "repository_metadata"
    assert result["repository"] == "psf/requests"


# ---------------------------------------------------------------------
# Issue Search
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_issue_search(agent):
    ctx = make_context(
        "issue_search",
        task="authentication bug",
    )

    result = await agent.execute(ctx)

    assert result["operation"] == "issue_search"
    assert result["query"] == "authentication bug"


# ---------------------------------------------------------------------
# Issue Analysis
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_issue_analysis(agent):
    ctx = make_context(
        "issue_analysis",
        issue=123,
    )

    result = await agent.execute(ctx)

    assert result["operation"] == "issue_analysis"
    assert result["issue"] == 123


# ---------------------------------------------------------------------
# Pull Request Review
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pull_request_review(agent):
    ctx = make_context(
        "pull_request_review",
        pull_request=45,
    )

    result = await agent.execute(ctx)

    assert result["operation"] == "pull_request_review"
    assert result["pull_request"] == 45


# ---------------------------------------------------------------------
# Pull Request Search
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pull_request_search(agent):
    ctx = make_context(
        "pull_request_search",
        task="bug fixes",
    )

    result = await agent.execute(ctx)

    assert result["operation"] == "pull_request_search"
    assert result["query"] == "bug fixes"


# ---------------------------------------------------------------------
# Commit History
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_commit_history(agent):
    ctx = make_context(
        "commit_history",
        repository="numpy/numpy",
    )

    result = await agent.execute(ctx)

    assert result["operation"] == "commit_history"
    assert result["repository"] == "numpy/numpy"


# ---------------------------------------------------------------------
# Release Information
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_release_information(agent):
    ctx = make_context(
        "release_information",
        repository="django/django",
    )

    result = await agent.execute(ctx)

    assert result["operation"] == "release_information"
    assert result["repository"] == "django/django"


# ---------------------------------------------------------------------
# Branch Information
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_branch_information(agent):
    ctx = make_context(
        "branch_information",
        repository="pallets/flask",
    )

    result = await agent.execute(ctx)

    assert result["operation"] == "branch_information"
    assert result["repository"] == "pallets/flask"


# ---------------------------------------------------------------------
# Code Search
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_code_search(agent):
    ctx = make_context(
        "code_search",
        task="async def execute",
    )

    result = await agent.execute(ctx)

    assert result["operation"] == "code_search"
    assert result["query"] == "async def execute"


# ---------------------------------------------------------------------
# Contributor Analysis
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_contributor_analysis(agent):
    ctx = make_context(
        "contributor_analysis",
        repository="microsoft/vscode",
    )

    result = await agent.execute(ctx)

    assert result["operation"] == "contributor_analysis"
    assert result["repository"] == "microsoft/vscode"


# ---------------------------------------------------------------------
# Repository Statistics
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_repository_statistics(agent):
    ctx = make_context(
        "repository_statistics",
        repository="keras-team/keras",
    )

    result = await agent.execute(ctx)

    assert result["operation"] == "repository_statistics"
    assert result["repository"] == "keras-team/keras"


# ---------------------------------------------------------------------
# Unsupported Capability
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_unsupported_capability(agent):
    ctx = make_context("unknown_capability")

    result = await agent.execute(ctx)

    assert result["success"] is False
    assert result["agent"] == "github"
    assert "Unsupported capability" in result["error"]


# ---------------------------------------------------------------------
# Test run() inherited from BaseAgent
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_method(agent):
    ctx = make_context(
        "repository_search",
        task="machine learning repositories",
    )

    result = await agent.run(ctx)

    assert result["success"] is True
    assert result["operation"] == "repository_search"