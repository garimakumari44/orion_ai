"""
Unit tests for PolicyEngine.

Tests
-----
- Enabled policy
- Capability policy
- Authentication policy
- Health policy
- Rate limit policy
- Full validation success
- Validation short-circuit behavior
"""

from unittest.mock import Mock

import pytest

from app.orchestration.capability import Capability
from app.orchestration.policies import PolicyEngine, PolicyResult


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def policy_engine():
    return PolicyEngine()


@pytest.fixture
def tool():
    tool = Mock()

    tool.name = "SearchTool"
    tool.enabled = True

    tool.capabilities = {
        
        Capability.WEB_SEARCH,
    }

    tool.requires_auth = False

    tool.is_authenticated.return_value = True
    tool.is_healthy.return_value = True
    tool.is_rate_limited.return_value = False

    return tool


# ------------------------------------------------------------------
# _check_enabled
# ------------------------------------------------------------------

def test_check_enabled_success(policy_engine, tool):
    result = policy_engine._check_enabled(tool)

    assert result.allowed is True
    assert result.reason is None


def test_check_enabled_failure(policy_engine, tool):
    tool.enabled = False

    result = policy_engine._check_enabled(tool)

    assert result.allowed is False
    assert "disabled" in result.reason.lower()


# ------------------------------------------------------------------
# _check_capability
# ------------------------------------------------------------------

def test_check_capability_success(policy_engine, tool):
    result = policy_engine._check_capability(
        tool,
        Capability.WEB_SEARCH,
    )

    assert result.allowed is True


def test_check_capability_failure(policy_engine, tool):
    result = policy_engine._check_capability(
        tool,
        Capability.CODE_SEARCH,
    )

    assert result.allowed is False
    assert "does not support" in result.reason.lower()


# ------------------------------------------------------------------
# _check_auth
# ------------------------------------------------------------------

def test_check_auth_not_required(policy_engine, tool):
    tool.requires_auth = False

    result = policy_engine._check_auth(tool)

    assert result.allowed is True


def test_check_auth_success(policy_engine, tool):
    tool.requires_auth = True
    tool.is_authenticated.return_value = True

    result = policy_engine._check_auth(tool)

    assert result.allowed is True


def test_check_auth_failure(policy_engine, tool):
    tool.requires_auth = True
    tool.is_authenticated.return_value = False

    result = policy_engine._check_auth(tool)

    assert result.allowed is False
    assert "authenticated" in result.reason.lower()


# ------------------------------------------------------------------
# _check_health
# ------------------------------------------------------------------

def test_check_health_success(policy_engine, tool):
    tool.is_healthy.return_value = True

    result = policy_engine._check_health(tool)

    assert result.allowed is True


def test_check_health_failure(policy_engine, tool):
    tool.is_healthy.return_value = False

    result = policy_engine._check_health(tool)

    assert result.allowed is False
    assert "unhealthy" in result.reason.lower()


# ------------------------------------------------------------------
# _check_rate_limit
# ------------------------------------------------------------------

def test_check_rate_limit_success(policy_engine, tool):
    tool.is_rate_limited.return_value = False

    result = policy_engine._check_rate_limit(tool)

    assert result.allowed is True


def test_check_rate_limit_failure(policy_engine, tool):
    tool.is_rate_limited.return_value = True

    result = policy_engine._check_rate_limit(tool)

    assert result.allowed is False
    assert "rate limited" in result.reason.lower()


# ------------------------------------------------------------------
# validate()
# ------------------------------------------------------------------

def test_validate_success(policy_engine, tool):
    result = policy_engine.validate(
        tool,
        Capability.WEB_SEARCH,
    )

    assert result.allowed is True
    assert result.reason is None


def test_validate_fails_when_disabled(policy_engine, tool):
    tool.enabled = False

    result = policy_engine.validate(
        tool,
        Capability.WEB_SEARCH,
    )

    assert result.allowed is False
    assert "disabled" in result.reason.lower()


def test_validate_fails_when_capability_missing(policy_engine, tool):
    result = policy_engine.validate(
        tool,
        Capability.CODE_SEARCH,
    )

    assert result.allowed is False
    assert "does not support" in result.reason.lower()


def test_validate_fails_when_authentication_missing(policy_engine, tool):
    tool.requires_auth = True
    tool.is_authenticated.return_value = False

    result = policy_engine.validate(
        tool,
        Capability.WEB_SEARCH,
    )

    assert result.allowed is False
    assert "authenticated" in result.reason.lower()


def test_validate_fails_when_unhealthy(policy_engine, tool):
    tool.is_healthy.return_value = False

    result = policy_engine.validate(
        tool,
        Capability.WEB_SEARCH,
    )

    assert result.allowed is False
    assert "unhealthy" in result.reason.lower()


def test_validate_fails_when_rate_limited(policy_engine, tool):
    tool.is_rate_limited.return_value = True

    result = policy_engine.validate(
        tool,
        Capability.WEB_SEARCH,
    )

    assert result.allowed is False
    assert "rate limited" in result.reason.lower()


# ------------------------------------------------------------------
# Short-circuit behavior
# ------------------------------------------------------------------

def test_validate_short_circuits_after_disabled(policy_engine, tool):
    tool.enabled = False

    policy_engine.validate(
        tool,
        Capability.WEB_SEARCH,
    )

    tool.is_authenticated.assert_not_called()
    tool.is_healthy.assert_not_called()
    tool.is_rate_limited.assert_not_called()


def test_validate_short_circuits_after_auth_failure(policy_engine, tool):
    tool.requires_auth = True
    tool.is_authenticated.return_value = False

    policy_engine.validate(
        tool,
        Capability.WEB_SEARCH,
    )

    tool.is_healthy.assert_not_called()
    tool.is_rate_limited.assert_not_called()