"""
Research Pipeline Template

Defines reusable research workflows.

Used by:
- Research Planner
- Knowledge Planner
- Equity Research Agents

Flow:

User Query
    |
    v
Research Planner
    |
    v
Task Graph

    Query Understanding
            |
            v
    Information Retrieval
            |
            v
    Source Validation
            |
            v
    Knowledge Extraction
            |
            v
    Research Synthesis
            |
            v
    Final Report
"""

from typing import List, Dict


def research_pipeline_template(
    query: str,
) -> List[Dict]:
    """
    Creates generic research workflow.
    """

    return [

        {
            "id": "understand_query",
            "name": "Understand Research Query",
            "agent": "research_planner",
            "task_type": "analysis",
            "description": query,
            "dependencies": []
        },


        {
            "id": "retrieve_information",
            "name": "Retrieve Information",
            "agent": "retrieval_agent",
            "task_type": "retrieval",
            "tools": [
                "web_search",
                "company_database"
            ],
            "dependencies": [
                "understand_query"
            ]
        },


        {
            "id": "validate_sources",
            "name": "Validate Sources",
            "agent": "validation_agent",
            "task_type": "verification",
            "dependencies": [
                "retrieve_information"
            ]
        },


        {
            "id": "extract_knowledge",
            "name": "Extract Research Facts",
            "agent": "knowledge_agent",
            "task_type": "knowledge_extraction",
            "dependencies": [
                "validate_sources"
            ]
        },


        {
            "id": "generate_report",
            "name": "Generate Research Report",
            "agent": "analysis_agent",
            "task_type": "generation",
            "dependencies": [
                "extract_knowledge"
            ]
        }

    ]