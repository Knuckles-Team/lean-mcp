"""R001: the receipt of `lean_check`."""

from __future__ import annotations

import json

import pytest

from lean_mcp.runner import Completed, LeanRefusal

from .conftest import VERSION_OUT, info, make_api

EXTRACT = "\n".join(
    json.dumps(r)
    for r in (
        {"t": "module", "name": "Proj", "imports": []},
        {"t": "decl", "name": "t", "kind": "theorem", "module": "Proj", "deps": []},
    )
)


def replies(axiom_line: str, build_out: str = "", build_code: int = 0) -> dict:
    return {
        ("env", "lean", "--version"): Completed(0, VERSION_OUT, ""),
        ("build",): Completed(build_code, build_out, ""),
        ("env", "lean", "--run"): Completed(0, EXTRACT, ""),
        ("env", "lean", "--json"): Completed(0, info(axiom_line), ""),
    }


# spec: CONN-LEAN-MCP-R001
def test_a_clean_proof_passes_with_standard_axioms(project):
    api, runner = make_api(
        project,
        replies("'t' depends on axioms: [propext, Classical.choice, Quot.sound]"),
    )
    receipt = api.check("proj", file="Proj.lean", declaration="t")
    assert receipt["verdict"] == "pass"
    assert receipt["has_sorry"] is False
    assert receipt["axioms"] == ["Classical.choice", "Quot.sound", "propext"]
    assert receipt["checker_id"] == "lean4"
    assert receipt["toolchain_version"] == "4.15.0"
    assert receipt["declaration"] == "t"
    assert len(receipt["artifact_digest"]) == 64
    assert ["build", "Proj"] in runner.calls


# spec: CONN-LEAN-MCP-R001
def test_sorry_fails_the_receipt(project):
    api, _ = make_api(
        project,
        replies(
            "'t' depends on axioms: [sorryAx]", "warning: declaration uses 'sorry'"
        ),
    )
    receipt = api.check("proj", file="Proj.lean", declaration="t")
    assert receipt["has_sorry"] is True
    assert receipt["verdict"] == "fail"


# spec: CONN-LEAN-MCP-R001
def test_nonstandard_axioms_are_reported(project):
    api, _ = make_api(project, replies("'t' depends on axioms: [propext, myAxiom]"))
    receipt = api.check("proj")
    assert receipt["verdict"] == "pass"
    assert "myAxiom" in receipt["axioms"]
    assert receipt["declaration"] == "proj"


# spec: CONN-LEAN-MCP-R001
def test_a_failed_build_fails_the_receipt(project):
    api, _ = make_api(project, replies("", "error: boom", build_code=1))
    assert api.check("proj", file="Proj.lean")["verdict"] == "fail"


# spec: CONN-LEAN-MCP-R001
def test_toolchain_mismatch_is_refused(project):
    (project / "lean-toolchain").write_text("leanprover/lean4:v4.9.0\n")
    api, _ = make_api(project, replies("'t' does not depend on any axioms"))
    with pytest.raises(LeanRefusal) as caught:
        api.check("proj")
    assert caught.value.code == "TOOLCHAIN_MISMATCH"


# spec: CONN-LEAN-MCP-R001
def test_paths_outside_the_workspace_are_refused(project):
    api, _ = make_api(project, replies(""))
    with pytest.raises(LeanRefusal) as caught:
        api.check("../elsewhere")
    assert caught.value.code == "PATH_OUTSIDE_WORKSPACE"
    with pytest.raises(LeanRefusal) as caught:
        api.check("proj", file="../x.lean")
    assert caught.value.code == "PATH_OUTSIDE_WORKSPACE"


# spec: CONN-LEAN-MCP-R001
def test_a_declaration_needs_a_file_and_a_plain_name(project):
    api, _ = make_api(project, replies(""))
    with pytest.raises(LeanRefusal) as caught:
        api.check("proj", declaration="t")
    assert caught.value.code == "DECLARATION_NEEDS_FILE"
    with pytest.raises(LeanRefusal) as caught:
        api.check("proj", file="Proj.lean", declaration="t; #eval 1")
    assert caught.value.code == "DECLARATION_INVALID"
