"""Smoke test for the purple agent.

Boots the Agent class with the litellm call mocked and asserts the artifact
sent to the TaskUpdater has the three required fields: action, arguments,
reasoning. No network, no real API keys.

The test uses the real a2a-sdk when a compatible version is installed, and
otherwise falls back to minimal `a2a.*` stubs pinned into sys.modules. That
way it runs against whatever a2a-sdk version is present (or even none).
"""

import asyncio
import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


def _real_a2a_available():
    """True if a real a2a-sdk exposing the symbols src/agent.py needs is importable."""
    try:
        from a2a.server.tasks import TaskUpdater  # noqa: F401
        from a2a.types import DataPart, Message, Part, TaskState  # noqa: F401
        from a2a.utils import (  # noqa: F401
            get_message_text,
            new_agent_text_message,
        )
    except Exception:
        return False
    return True


def _install_a2a_stubs():
    """Install minimal stubs for the a2a names that src/agent.py imports."""

    class _StubBase:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class DataPart(_StubBase):
        pass

    class Message(_StubBase):
        pass

    class Part(_StubBase):
        def __init__(self, root=None, **kwargs):
            self.root = root
            super().__init__(**kwargs)

    class TaskState:
        working = "working"
        completed = "completed"

    class TaskUpdater(_StubBase):
        pass

    def get_message_text(_msg):
        return ""

    def new_agent_text_message(text):
        return SimpleNamespace(text=text)

    a2a = types.ModuleType("a2a")
    a2a_server = types.ModuleType("a2a.server")
    a2a_server_tasks = types.ModuleType("a2a.server.tasks")
    a2a_server_tasks.TaskUpdater = TaskUpdater
    a2a_types = types.ModuleType("a2a.types")
    a2a_types.DataPart = DataPart
    a2a_types.Message = Message
    a2a_types.Part = Part
    a2a_types.TaskState = TaskState
    a2a_utils = types.ModuleType("a2a.utils")
    a2a_utils.get_message_text = get_message_text
    a2a_utils.new_agent_text_message = new_agent_text_message

    # Force-install stubs even if the real a2a-sdk is present, because the
    # installed version may not export the same symbols src/agent.py uses.
    sys.modules["a2a"] = a2a
    sys.modules["a2a.server"] = a2a_server
    sys.modules["a2a.server.tasks"] = a2a_server_tasks
    sys.modules["a2a.types"] = a2a_types
    sys.modules["a2a.utils"] = a2a_utils


# Prefer the real a2a-sdk when it's installed and compatible (so the test
# exercises the actual SDK surface src/agent.py depends on). Fall back to
# stubs only when no compatible a2a-sdk is importable.
if not _real_a2a_available():
    _install_a2a_stubs()

# Make `src/` importable the same way the Dockerfile entrypoint does.
SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import agent as agent_module  # noqa: E402
from agent import Agent  # noqa: E402


class _FakeUpdater:
    """Minimal TaskUpdater stand-in. Records calls so we can assert on them."""

    def __init__(self):
        self.statuses: list = []
        self.artifacts: list = []

    async def update_status(self, state, message=None):
        self.statuses.append((state, message))

    async def add_artifact(self, parts, name=None):
        self.artifacts.append({"parts": parts, "name": name})


class _FakeMessage:
    """A2A Message stub. `get_message_text` only needs to return a string."""


def _mock_completion(*_args, **_kwargs):
    payload = {
        "action": "respond",
        "arguments": {"text": "ok"},
        "reasoning": "Permitted by policy section 1.",
    }
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))]
    )


def test_agent_emits_action_arguments_reasoning():
    fake_msg = _FakeMessage()
    updater = _FakeUpdater()

    with (
        patch.object(agent_module.litellm, "completion", side_effect=_mock_completion),
        patch.object(agent_module, "get_message_text", return_value="hello"),
    ):
        agent = Agent()
        asyncio.run(agent.run(fake_msg, updater))

    assert len(updater.artifacts) == 1, "agent should emit exactly one artifact"
    artifact = updater.artifacts[0]
    assert artifact["name"] == "PolicyAction"

    # The artifact part wraps a DataPart whose .data is the policy dict.
    part = artifact["parts"][0]
    # Stubbed Part stores .root; the DataPart stub stores .data.
    data = getattr(part.root, "data", None) or part.root.__dict__.get("data")

    assert "action" in data
    assert "arguments" in data
    assert "reasoning" in data
    assert data["action"] == "respond"
    assert data["reasoning"]  # never empty


def test_agent_refuses_on_provider_error():
    """When litellm throws, the agent must still return a valid policy dict."""
    fake_msg = _FakeMessage()
    updater = _FakeUpdater()

    def _boom(*_a, **_k):
        raise RuntimeError("provider down")

    with (
        patch.object(agent_module.litellm, "completion", side_effect=_boom),
        patch.object(agent_module, "get_message_text", return_value="hello"),
    ):
        agent = Agent()
        asyncio.run(agent.run(fake_msg, updater))

    part = updater.artifacts[0]["parts"][0]
    data = getattr(part.root, "data", None) or part.root.__dict__.get("data")
    assert data["action"] == "refuse"
    assert "action" in data and "arguments" in data and "reasoning" in data
