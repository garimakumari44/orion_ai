from __future__ import annotations

from datetime import datetime, timedelta

from app.orchestration.health_monitor import (
    HealthMonitor,
    ToolHealth,
)


# ============================================================
# Registration
# ============================================================

def test_register_tool():
    monitor = HealthMonitor()

    monitor.register_tool("github")

    health = monitor.get_health("github")

    assert isinstance(health, ToolHealth)
    assert health.tool_name == "github"
    assert health.total_calls == 0
    assert health.healthy is True


# ============================================================
# Success Recording
# ============================================================

def test_record_success_updates_statistics():
    monitor = HealthMonitor()

    monitor.record_success("github", latency=0.5)

    health = monitor.get_health("github")

    assert health.total_calls == 1
    assert health.successful_calls == 1
    assert health.failed_calls == 0
    assert health.total_latency == 0.5
    assert health.average_latency == 0.5
    assert health.success_rate == 1.0
    assert health.consecutive_failures == 0
    assert health.healthy is True
    assert health.disabled_until is None


def test_multiple_successes_average_latency():
    monitor = HealthMonitor()

    monitor.record_success("github", 1.0)
    monitor.record_success("github", 3.0)

    health = monitor.get_health("github")

    assert health.total_calls == 2
    assert health.successful_calls == 2
    assert health.average_latency == 2.0


# ============================================================
# Failure Recording
# ============================================================

def test_record_failure_updates_statistics():
    monitor = HealthMonitor(failure_threshold=3)

    monitor.record_failure("browser", "Timeout")

    health = monitor.get_health("browser")

    assert health.total_calls == 1
    assert health.failed_calls == 1
    assert health.successful_calls == 0
    assert health.consecutive_failures == 1
    assert health.last_error == "Timeout"
    assert health.healthy is True


def test_failure_threshold_disables_tool():
    monitor = HealthMonitor(
        failure_threshold=2,
        cooldown_seconds=60,
    )

    monitor.record_failure("browser", "Error 1")
    monitor.record_failure("browser", "Error 2")

    health = monitor.get_health("browser")

    assert health.failed_calls == 2
    assert health.consecutive_failures == 2
    assert health.healthy is False
    assert health.disabled_until is not None


# ============================================================
# Health Checks
# ============================================================

def test_is_healthy_returns_true_for_new_tool():
    monitor = HealthMonitor()

    assert monitor.is_healthy("new_tool") is True


def test_is_healthy_returns_false_when_disabled():
    monitor = HealthMonitor(
        failure_threshold=1,
        cooldown_seconds=60,
    )

    monitor.record_failure("browser", "Crash")

    assert monitor.is_healthy("browser") is False


def test_tool_recovers_after_cooldown():
    monitor = HealthMonitor(
        failure_threshold=1,
        cooldown_seconds=60,
    )

    monitor.record_failure("browser", "Crash")

    health = monitor.get_health("browser")

    # Simulate cooldown expiration
    health.disabled_until = datetime.utcnow() - timedelta(seconds=1)

    assert monitor.is_healthy("browser") is True

    assert health.healthy is True
    assert health.consecutive_failures == 0
    assert health.disabled_until is None


# ============================================================
# Success After Failure
# ============================================================

def test_success_resets_failure_count():
    monitor = HealthMonitor()

    monitor.record_failure("github", "Timeout")
    monitor.record_success("github", latency=0.4)

    health = monitor.get_health("github")

    assert health.consecutive_failures == 0
    assert health.healthy is True
    assert health.successful_calls == 1
    assert health.failed_calls == 1


# ============================================================
# Health Retrieval
# ============================================================

def test_get_all_health_returns_all_tools():
    monitor = HealthMonitor()

    monitor.record_success("github", 0.2)
    monitor.record_success("browser", 0.5)

    tools = monitor.get_all_health()

    assert len(tools) == 2

    names = {tool.tool_name for tool in tools}

    assert names == {"github", "browser"}


# ============================================================
# Reset
# ============================================================

def test_reset_tool():
    monitor = HealthMonitor()

    monitor.record_success("github", 1.2)
    monitor.record_failure("github", "Timeout")

    monitor.reset("github")

    health = monitor.get_health("github")

    assert health.total_calls == 0
    assert health.successful_calls == 0
    assert health.failed_calls == 0
    assert health.total_latency == 0
    assert health.consecutive_failures == 0
    assert health.healthy is True


def test_reset_all():
    monitor = HealthMonitor()

    monitor.record_success("github", 1.0)
    monitor.record_failure("browser", "Crash")

    monitor.reset_all()

    github = monitor.get_health("github")
    browser = monitor.get_health("browser")

    assert github.total_calls == 0
    assert browser.total_calls == 0

    assert github.healthy is True
    assert browser.healthy is True


# ============================================================
# ToolHealth Properties
# ============================================================

def test_average_latency_zero_calls():
    health = ToolHealth("github")

    assert health.average_latency == 0.0


def test_success_rate_zero_calls():
    health = ToolHealth("github")

    assert health.success_rate == 1.0


def test_success_rate_calculation():
    health = ToolHealth("github")

    health.total_calls = 5
    health.successful_calls = 4

    assert health.success_rate == 0.8