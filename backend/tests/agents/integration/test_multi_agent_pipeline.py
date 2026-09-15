"""
Integration tests for the complete multi-agent pipeline.

Pipeline

AgentContext
      │
      ▼
ResearchAgent
      │
      ▼
CodeAgent
      │
      ▼
CriticAgent
      │
      ▼
WriterAgent

Verifies that

- agents execute successfully
- shared context propagates
- metadata flows through the pipeline
- final report is generated
- critic validates the report
"""

from __future__ import annotations

import pytest

from app.agents.base.agent_context import AgentContext
from app.agents.research.research_agent import ResearchAgent
from app.agents.code.code_agent import CodeAgent
from app.agents.critic.critic_agent import CriticAgent
from app.agents.writer.writer_agent import WriterAgent


@pytest.mark.asyncio
async def test_multi_agent_pipeline():

    context = AgentContext(
        query="Build an AI workflow orchestration platform",
        task="Design Orion AI",
    )

    research_agent = ResearchAgent()
    code_agent = CodeAgent()
    critic_agent = CriticAgent()
    writer_agent = WriterAgent()

    # ---------------------------------------------------------
    # Stage 1 : Research
    # ---------------------------------------------------------

    research_result = await research_agent.run(context)

    assert research_result is not None
    assert research_result["agent"] == "research"
    assert research_result["status"] == "completed"
    assert research_result["query"] == context.task

    context.metadata["research"] = research_result["summary"]

    # ---------------------------------------------------------
    # Stage 2 : Code
    # ---------------------------------------------------------

    code_result = await code_agent.run(context)

    assert code_result is not None
    assert code_result["success"] is True
    assert code_result["agent"] == "code"
    assert code_result["task"] == context.task

    context.metadata["code"] = code_result["output"]

    # ---------------------------------------------------------
    # Stage 3 : Shared synthesized result
    # ---------------------------------------------------------

    context.metadata["synthesized_result"] = (
        "Research completed successfully. "
        "Implementation strategy prepared."
    )

    # ---------------------------------------------------------
    # Stage 4 : Writer
    # ---------------------------------------------------------

    writer_result = await writer_agent.run(context)

    assert writer_result is not None
    assert writer_result["success"] is True
    assert writer_result["agent"] == "writer"

    report = writer_result["result"]

    assert isinstance(report, str)

    assert "# Final Report" in report
    assert "## Task" in report
    assert "Design Orion AI" in report

    assert "## Summary" in report

    assert (
        "Research completed successfully."
        in report
    )

    assert "## Code" in report

    # ---------------------------------------------------------
    # Stage 5 : Critic
    # ---------------------------------------------------------

    context.metadata["output"] = report

    critic_result = await critic_agent.run(context)

    assert critic_result is not None
    assert critic_result["success"] is True
    assert critic_result["agent"] == "critic"

    review = critic_result["review"]

    assert isinstance(review, dict)

    assert "score" in review
    assert "summary" in review
    assert "strengths" in review
    assert "issues" in review
    assert "suggestions" in review

    assert review["score"] >= 0

    # ---------------------------------------------------------
    # Context validation
    # ---------------------------------------------------------

    assert context.metadata["research"] == research_result["summary"]

    assert context.metadata["code"] == code_result["output"]

    assert context.metadata["output"] == report

    assert context.errors == []