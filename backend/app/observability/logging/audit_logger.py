"""
audit_logger.py

Audit trail logging for AI systems.

Tracks:
- User actions
- Agent decisions
- Tool executions
- Configuration changes
- Security events
"""


from typing import Any, Dict, Optional
from datetime import datetime, timezone

from .logger import get_logger


logger = get_logger("audit")


class AuditLogger:
    """
    Enterprise audit logger.
    """


    def __init__(self):

        self.logger = logger



    def log_event(
        self,
        *,
        event_type: str,
        actor_id: Optional[str] = None,
        request_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Generic audit event.

        Example events:

        user.login
        llm.request
        agent.tool_execution
        config.updated
        """

        event = {

            "event": "audit",

            "event_type": event_type,

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "actor_id":
                actor_id,

            "request_id":
                request_id,

            "resource":
                resource,

            "action":
                action,

            "details":
                details or {}
        }


        self.logger.info(
            "Audit event",
            extra=event
        )



    def log_llm_decision(
        self,
        *,
        request_id: str,
        agent: str,
        model: str,
        decision: str,
        reasoning_summary: Optional[str] = None,
    ):
        """
        Record AI decision metadata.

        Important:
        Store summary only.
        Avoid storing private chain-of-thought.
        """

        self.logger.info(
            "AI decision recorded",

            extra={

                "event":
                    "ai_decision",

                "request_id":
                    request_id,

                "agent":
                    agent,

                "model":
                    model,

                "decision":
                    decision,

                "reasoning_summary":
                    reasoning_summary

            }
        )



    def log_tool_execution(
        self,
        *,
        request_id: str,
        tool_name: str,
        status: str,
        input_schema: Dict[str, Any],
        output_summary: Optional[str] = None,
    ):
        """
        Log agent tool usage.
        """

        self.logger.info(

            "Tool execution",

            extra={

                "event":
                    "tool_execution",

                "request_id":
                    request_id,

                "tool":
                    tool_name,

                "status":
                    status,

                "input":
                    input_schema,

                "output_summary":
                    output_summary
            }
        )



    def log_security_event(
        self,
        *,
        event_name: str,
        severity: str,
        details: Dict[str, Any]
    ):
        """
        Security-related events.

        Examples:

        pii_detected
        prompt_injection_blocked
        unsafe_request
        """

        self.logger.warning(

            "Security event",

            extra={

                "event":
                    "security",

                "event_name":
                    event_name,

                "severity":
                    severity,

                "details":
                    details

            }
        )