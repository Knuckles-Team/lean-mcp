"""One real check on the fixture projects. Skipped when `lake` is not installed."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from lean_mcp.api_client import Api
from lean_mcp.runner import LeanRunner

FIXTURES = Path(__file__).parent / "fixtures"
pytestmark = pytest.mark.skipif(
    shutil.which("lake") is None, reason="the Lean toolchain is not installed"
)


# spec: CONN-LEAN-MCP-R001
def test_real_check_passes_a_clean_declaration():
    api = Api(LeanRunner(FIXTURES, timeout_s=900))
    receipt = api.check("tiny", file="Tiny.lean", declaration="double_eq")
    assert receipt["verdict"] == "pass"
    assert receipt["has_sorry"] is False


# spec: CONN-LEAN-MCP-R001
def test_real_check_fails_a_sorry():
    api = Api(LeanRunner(FIXTURES, timeout_s=900))
    receipt = api.check("tiny_sorry", file="TinySorry.lean", declaration="unfinished")
    assert receipt["has_sorry"] is True
    assert receipt["verdict"] == "fail"


# spec: CONN-LEAN-MCP-R002
def test_real_extract_lists_declarations_and_edges():
    api = Api(LeanRunner(FIXTURES, timeout_s=900))
    out = api.extract("tiny")
    kinds = {d["name"]: d["kind"] for d in out["declarations"]}
    assert kinds["double"] == "definition"
    assert kinds["double_eq"] == "theorem"
    assert {"from": "double_eq", "to": "double", "predicate": "dependsOn"} in out[
        "edges"
    ]
