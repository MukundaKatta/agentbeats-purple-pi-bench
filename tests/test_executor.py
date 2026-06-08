"""Tests for the A2A executor.

These run only when a compatible a2a-sdk is installed, because the executor's
control flow (start_work -> agent.run -> complete, or -> failed on error) is
tied to the real TaskUpdater API. The smoke test covers the stub-only path.

Regression target: the executor must call ``TaskUpdater.failed`` (not a
nonexistent ``fail``) when the agent raises, otherwise the error handler would
itself crash with AttributeError and swallow the original failure.
"""

import asyncio
import sys
from pathlib import Path

import pytest

# Only meaningful against the real SDK; skip cleanly otherwise.
a2a = pytest.importorskip("a2a")
try:
    from a2a.server.tasks import TaskUpdater
    from a2a.types import Message, Part, Role, TextPart
except Exception:  # pragma: no cover - incompatible SDK version
    pytest.skip("incompatible a2a-sdk version", allow_module_level=True)

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import executor as executor_module  # noqa: E402
from executor import Executor  # noqa: E402


class _RecordingUpdater:
    """Stand-in for TaskUpdater that records terminal-state calls."""

    def __init__(self):
        self.started = False
        self.completed = False
        self.failed_message = None
        self.artifacts = []
        self._terminal_state_reached = False

    async def start_work(self, message=None):
        self.started = True

    async def update_status(self, state, message=None, **kwargs):
        pass

    async def add_artifact(self, parts, name=None, **kwargs):
        self.artifacts.append({"parts": parts, "name": name})

    async def complete(self, message=None):
        self.completed = True
        self._terminal_state_reached = True

    async def failed(self, message=None):
        self.failed_message = message
        self._terminal_state_reached = True


def _user_message():
    return Message(
        message_id="m1",
        role=Role.user,
        parts=[Part(root=TextPart(text="hi"))],
    )


def _run_execute(executor, context, updater):
    """Drive Executor.execute with a fake event queue and patched TaskUpdater."""

    class _FakeQueue:
        def __init__(self):
            self.events = []

        async def enqueue_event(self, event):
            self.events.append(event)

    queue = _FakeQueue()

    # Patch the TaskUpdater the executor constructs internally.
    import unittest.mock as mock

    with mock.patch.object(executor_module, "TaskUpdater", return_value=updater):
        asyncio.run(executor.execute(context, queue))
    return queue


def test_executor_completes_on_success():
    class _StubAgent:
        async def run(self, msg, updater):
            await updater.add_artifact(parts=[], name="PolicyAction")

    executor = Executor()
    context = type("Ctx", (), {"message": _user_message(), "current_task": None})()
    updater = _RecordingUpdater()

    import unittest.mock as mock

    with mock.patch.object(executor_module, "Agent", _StubAgent):
        _run_execute(executor, context, updater)

    assert updater.started is True
    assert updater.completed is True
    assert updater.failed_message is None


def test_executor_calls_failed_on_agent_error():
    """The fix: an agent error must route to TaskUpdater.failed, not crash."""

    class _BoomAgent:
        async def run(self, msg, updater):
            raise RuntimeError("kaboom")

    executor = Executor()
    context = type("Ctx", (), {"message": _user_message(), "current_task": None})()
    updater = _RecordingUpdater()

    import unittest.mock as mock

    with mock.patch.object(executor_module, "Agent", _BoomAgent):
        _run_execute(executor, context, updater)

    assert updater.completed is False
    # A real Message was passed (not a bare string) and it carries the error.
    assert isinstance(updater.failed_message, Message)
    text = "".join(
        getattr(p.root, "text", "") for p in (updater.failed_message.parts or [])
    )
    assert "RuntimeError" in text and "kaboom" in text


def test_taskupdater_has_failed_not_fail():
    """Guards against regressing to the nonexistent TaskUpdater.fail name."""
    assert hasattr(TaskUpdater, "failed")
    assert not hasattr(TaskUpdater, "fail")
