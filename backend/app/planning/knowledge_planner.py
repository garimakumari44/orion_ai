from __future__ import annotations

import uuid

from app.planning.models.task import (
    Task,
    TaskType,
    TaskPriority,
)


class KnowledgePlanner:
    """
    Generates tasks for knowledge/retrieval workflows.

    The planner describes the required capability and
    explicitly identifies the executor responsible for
    performing that capability.
    """

    def __init__(self):
        pass

    def plan(self, request) -> list[Task]:
        query = getattr(request, "query", "") or ""

        entity_task = Task(
            id=str(uuid.uuid4()),
            title="Resolve Entities",
            description="Resolve entities from the research query.",
            task_type=TaskType.RETRIEVE,
            capability="entity.resolve",
            priority=TaskPriority.HIGH,
            assigned_executor="knowledge",
            parameters={
                "query": query,
            },
            dependencies=[],
        )

        knowledge_task = Task(
            id=str(uuid.uuid4()),
            title="Retrieve Knowledge",
            description="Retrieve relevant documents and evidence.",
            task_type=TaskType.RETRIEVE,
            capability="knowledge.retrieve",
            priority=TaskPriority.HIGH,
            assigned_executor="knowledge",
            parameters={
                "query": query,
            },
            dependencies=[
                entity_task.id,
            ],
        )

        enrichment_task = Task(
            id=str(uuid.uuid4()),
            title="Enrich Knowledge",
            description="Enrich retrieved information with relevant context.",
            task_type=TaskType.ANALYZE,
            capability="knowledge.enrich",
            priority=TaskPriority.MEDIUM,
            assigned_executor="knowledge",
            parameters={
                "query": query,
            },
            dependencies=[
                knowledge_task.id,
            ],
        )

        reasoning_task = Task(
            id=str(uuid.uuid4()),
            title="Reason Over Knowledge",
            description="Infer relationships and research-relevant insights.",
            task_type=TaskType.REASON,
            capability="knowledge.reason",
            priority=TaskPriority.MEDIUM,
            assigned_executor="knowledge",
            parameters={
                "query": query,
            },
            dependencies=[
                enrichment_task.id,
            ],
        )

        summary_task = Task(
            id=str(uuid.uuid4()),
            title="Summarize Findings",
            description="Generate a concise summary of the findings.",
            task_type=TaskType.SUMMARIZE,
            capability="knowledge.summarize",
            priority=TaskPriority.MEDIUM,
            assigned_executor="knowledge",
            parameters={
                "query": query,
            },
            dependencies=[
                reasoning_task.id,
            ],
        )

        return [
            entity_task,
            knowledge_task,
            enrichment_task,
            reasoning_task,
            summary_task,
        ]