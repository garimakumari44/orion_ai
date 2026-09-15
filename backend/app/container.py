from __future__ import annotations

"""
Application Composition Root.

Responsible for constructing and wiring together all
application services.

Nothing outside this module should manually instantiate
core services.
"""

from app.agents.manager.agent_manager import AgentManager


from app.execution.dispatcher import Dispatcher
from app.execution.execution_engine import ExecutionEngine
from app.execution.executor import Executor
from app.execution.worker import Worker

from app.planning.planner import Planner
from app.services.planner_service import PlannerService
from app.orchestration.tool_registry  import ToolRegistry
from app.orchestration.policies  import PolicyEngine
from app.orchestration.health_monitor  import HealthMonitor
from app.orchestration.orchestration_service  import OrchestrationService


# =========================================================
# Memory
# =========================================================

from app.memory.manager import MemoryManager
from app.memory.services.memory_service import MemoryService




class ApplicationContainer:
    """
    Dependency Injection Container.

    Creates all long-lived application services once
    and exposes them for the rest of the application.
    """


    def __init__(self) -> None:

        self.registry = ToolRegistry()

        

        self.health_monitor = HealthMonitor()

        self.policy_engine = PolicyEngine()
        
        self.orchestration_service = OrchestrationService(
    registry=self.registry,
    selector=self.selector,
    health_monitor=self.health_monitor,
    policy_engine=self.policy_engine
)
        # =====================================================
        # Memory Layer
        # =====================================================

        self.memory_manager = MemoryManager()

        self.memory_service = MemoryService(
            manager=self.memory_manager,
        )


        # =====================================================
        # Registries
        # =====================================================

        



        # =====================================================
        # Agent Layer
        # =====================================================

       


        self.agent_manager = AgentManager(
            selector=self.agent_selector,
            registry=self.capability_registry,
        )



        # =====================================================
        # Execution Layer
        # =====================================================

        self.worker = Worker(
            agent_manager=self.agent_manager,
            memory_service=self.memory_service,
        )


        self.dispatcher = Dispatcher(
            worker=self.worker,
        )


        self.execution_engine = ExecutionEngine(
            dispatcher=self.dispatcher,
        )


        self.executor = Executor(
            engine=self.execution_engine,
        )



        # =====================================================
        # Planning Layer
        # =====================================================

        self.planner = Planner(
            memory_service=self.memory_service,
        )


        self.planner_service = PlannerService(
            planner=self.planner,
            executor=self.executor,
            memory_service=self.memory_service,
        )



# Singleton container used by the application.

container = ApplicationContainer()