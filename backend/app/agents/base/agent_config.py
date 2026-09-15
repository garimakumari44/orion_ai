from dataclasses import dataclass


@dataclass
class AgentConfig:

    name: str

    description: str

    version: str = "1.0"

    enabled: bool = True

    max_retries: int = 3

    timeout: int = 300