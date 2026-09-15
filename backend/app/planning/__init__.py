"""
Planning Module

This package converts a user request into an executable
dependency graph for the Multi-Agent AI Analyst.

Pipeline

User Query
      │
      ▼
Parser
      │
      ▼
Planner
      │
      ▼
Task Graph Builder
      │
      ▼
Graph Validator
      │
      ▼
Scheduler
      │
      ▼
Execution Plan
      │
      ▼
Agent Executor

The planning system is deterministic.

LLMs are only used where reasoning is required.

Responsibilities
----------------
- Parse intent
- Create logical tasks
- Build dependency graph
- Validate DAG
- Schedule execution
- Produce execution plan

This package never executes agents.
"""

from .parser import PlanningParser
from .planner import Planner
from .graph_builder import GraphBuilder
from .validator import GraphValidator
from .scheduler import Scheduler
from .models.execution_plan import ExecutionPlan


__all__ = [
    "PlanningParser",
    "Planner",
    "GraphBuilder",
    "GraphValidator",
    "Scheduler",
    "ExecutionPlan",
    
]