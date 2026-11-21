"""R002: declaration and dependency extraction."""

from __future__ import annotations

import json

import pytest

from lean_mcp.runner import Completed, LeanRefusal

from .conftest import VERSION_OUT, make_api

LINES = [
    {"t": "module", "name": "Proj", "imports": ["Proj.Basic", "Init"]},
    {"t": "module", "name": "Proj.Basic", "imports": []},
    {
        "t": "decl",
        "name": "Proj.b",
        "kind": "theorem",
        "module": "Proj",
        "deps": ["Proj.a"],
    },
    {
        "t": "decl",
        "name": "Proj.a",
        "kind": "definition",
        "module": "Proj.Basic",
        "deps": [],
    },
]


# spec: CONN-LEAN-MCP-R002
def test_extract_returns_declarations_and_edges(project):
    (project / "Proj").mkdir()
    (project / "Proj" / "Basic.lean").write_text("def a := 1\n")
    api, runner = make_api(
        project,
        {
            ("env", "lean", "--version"): Completed(0, VERSION_OUT, ""),
            ("env", "lean", "--run"): Completed(
                0, "\n".join(json.dumps(r) for r in LINES), ""
            ),
        },
    )
    out = api.extract("proj")
    assert out["modules"] == ["Proj", "Proj.Basic"]
    assert [d["name"] for d in out["declarations"]] == ["Proj.a", "Proj.b"]
    assert out["edges"] == [
        {"from": "Proj.b", "to": "Proj.a", "predicate": "dependsOn"}
    ]
    assert out["module_edges"] == [{"from": "Proj", "to": "Proj.Basic"}]
    run_call = next(c for c in runner.calls if c[:3] == ["env", "lean", "--run"])
    assert run_call[-2:] == ["Proj", "Proj.Basic"]


# spec: CONN-LEAN-MCP-R002
def test_a_failed_build_is_refused(project):
    api, _ = make_api(
        project,
        {
            ("env", "lean", "--version"): Completed(0, VERSION_OUT, ""),
            ("build",): Completed(1, "", "error"),
        },
    )
    with pytest.raises(LeanRefusal) as caught:
        api.extract("proj")
    assert caught.value.code == "BUILD_FAILED"


# spec: CONN-LEAN-MCP-R002
def test_a_failed_extraction_script_is_refused(project):
    api, _ = make_api(
        project,
        {
            ("env", "lean", "--version"): Completed(0, VERSION_OUT, ""),
            ("env", "lean", "--run"): Completed(1, "", "unknown module"),
        },
    )
    with pytest.raises(LeanRefusal) as caught:
        api.extract("proj")
    assert caught.value.code == "EXTRACT_FAILED"
