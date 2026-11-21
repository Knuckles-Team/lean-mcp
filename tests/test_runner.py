"""R001: every call is a bounded subprocess."""

from __future__ import annotations

import time

import pytest

from lean_mcp.runner import LeanRefusal, LeanRunner


# spec: CONN-LEAN-MCP-R001
def test_a_timeout_kills_the_process_and_refuses(tmp_path):
    runner = LeanRunner(tmp_path, timeout_s=1, lake="sleep")
    start = time.monotonic()
    with pytest.raises(LeanRefusal) as caught:
        runner.run(["30"], tmp_path)
    assert caught.value.code == "CHECK_TIMEOUT"
    assert time.monotonic() - start < 10


# spec: CONN-LEAN-MCP-R001
def test_a_missing_toolchain_is_refused(tmp_path):
    runner = LeanRunner(tmp_path, lake="lake-that-does-not-exist")
    with pytest.raises(LeanRefusal) as caught:
        runner.run(["build"], tmp_path)
    assert caught.value.code == "TOOLCHAIN_MISSING"


# spec: CONN-LEAN-MCP-R001
def test_the_environment_is_minimal(tmp_path, monkeypatch):
    monkeypatch.setenv("LEAN_SECRET_TOKEN", "x")
    runner = LeanRunner(tmp_path, lake="env")
    done = runner.run([], tmp_path)
    assert "LEAN_SECRET_TOKEN" not in done.stdout
