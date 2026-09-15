"""
Agent Metadata

Defines metadata used by the registry
for routing and orchestration.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Type


@dataclass(slots=True)
class AgentMetadata:
    """
    Metadata describing an agent.
    """

    agent_id: str

    agent_class: Type

    category: str

    display_name: Optional[str] = None

    description: str = ""

    capabilities: List[str] = field(default_factory=list)

    dependencies: List[str] = field(default_factory=list)

    enabled: bool = True