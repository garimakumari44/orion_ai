"""
Tool Execution Context

Carries runtime information during tool execution.

Examples:
- Which agent called the tool
- User request
- Company being analyzed
- Research task id
- Execution metadata

Used by:
- Tool Router
- Agents
- Execution Engine
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import uuid



@dataclass
class ToolContext:
    """
    Shared context for all tools.
    """

    request_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )


    user_query: Optional[str] = None


    agent_name: Optional[str] = None


    company: Optional[str] = None


    ticker: Optional[str] = None


    task_id: Optional[str] = None


    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


    created_at: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )


    def add_metadata(
        self,
        key: str,
        value: Any
    ):
        """
        Add runtime metadata.
        """

        self.metadata[key] = value



    def to_dict(self):

        return {

            "request_id": self.request_id,

            "user_query": self.user_query,

            "agent_name": self.agent_name,

            "company": self.company,

            "ticker": self.ticker,

            "task_id": self.task_id,

            "metadata": self.metadata,

            "created_at": self.created_at

        }