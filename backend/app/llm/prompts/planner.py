"""
Planner prompts.

This module contains prompt templates for the Equity Research
Planning Agent.

The Planning Agent is responsible for decomposing user requests
into executable multi-agent workflows.

It never performs research or analysis itself.
"""

from textwrap import dedent
from typing import List, Optional


class PlannerPrompts:
    """Prompt templates for the Planning Agent."""

    @staticmethod
    def system_prompt() -> str:
        return dedent(
            """
            You are an expert Equity Research Planning Agent.

            Your only responsibility is planning.

            Responsibilities

            - Understand the user's investment objective.
            - Identify required specialist agents.
            - Build an execution workflow.
            - Determine dependencies.
            - Determine execution order.
            - Assign priorities.
            - Select required tools.
            - Never execute tasks.
            - Never analyze companies.
            - Never make investment recommendations.

            Available specialist agents may include

            - Retrieval Agent
            - Research Agent
            - Financial Analysis Agent
            - Valuation Agent
            - Industry Analysis Agent
            - Competitor Analysis Agent
            - Risk Analysis Agent
            - Investment Memo Agent
            - Writer Agent

            Every task must include

            - id
            - agent
            - description
            - reasoning
            - tool
            - dependencies
            - priority

            Return JSON only.
            """
        ).strip()

    @staticmethod
    def planning_prompt(
        user_query: str,
        available_tools: Optional[List[str]] = None,
        memory_context: Optional[str] = None,
    ) -> str:

        tools = (
            "\n".join(f"- {tool}" for tool in available_tools)
            if available_tools
            else "No external tools available."
        )

        memory = memory_context or "No relevant memory."

        return dedent(
            f"""
            User Request

            {user_query}

            ------------------------------------

            Available Tools

            {tools}

            ------------------------------------

            Memory

            {memory}

            ------------------------------------

            Build the optimal multi-agent execution plan.

            Planning Guidelines

            1. Understand the user's objective.
            2. Determine required specialist agents.
            3. Create logical execution order.
            4. Define task dependencies.
            5. Assign tools.
            6. Assign priorities.
            7. Skip unnecessary agents.
            8. Return JSON only.

            Example workflow

            Retrieval
                ↓
            Research
                ↓
            Financial Analysis
                ↓
            Industry Analysis
                ↓
            Competitor Analysis
                ↓
            Valuation
                ↓
            Risk Analysis
                ↓
            Investment Memo
                ↓
            Writer

            Return JSON

            {{
                "goal": "",
                "workflow": [],
                "tasks": [
                    {{
                        "id": "",
                        "agent": "",
                        "description": "",
                        "reasoning": "",
                        "tool": "",
                        "dependencies": [],
                        "priority": 1
                    }}
                ]
            }}
            """
        ).strip()

    @staticmethod
    def replan_prompt(
        original_goal: str,
        completed_tasks: List[str],
        failed_tasks: List[str],
    ) -> str:

        completed = "\n".join(f"- {t}" for t in completed_tasks) or "None"
        failed = "\n".join(f"- {t}" for t in failed_tasks) or "None"

        return dedent(
            f"""
            Original Goal

            {original_goal}

            ------------------------------------

            Completed Tasks

            {completed}

            ------------------------------------

            Failed Tasks

            {failed}

            ------------------------------------

            Generate an updated execution plan.

            Requirements

            - Preserve completed tasks.
            - Replace failed tasks when possible.
            - Reorder workflow if necessary.
            - Keep dependencies valid.
            - Return JSON only.

            {{
                "updated_workflow": [],
                "tasks": []
            }}
            """
        ).strip()

    @staticmethod
    def summarize_plan_prompt(plan_json: str) -> str:

        return dedent(
            f"""
            Explain the following multi-agent execution plan
            in simple language.

            Plan

            {plan_json}

            Describe

            - overall objective
            - execution stages
            - specialist agents involved
            - expected final output

            Keep the explanation concise and user-friendly.
            """
        ).strip()