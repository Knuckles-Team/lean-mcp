"""R003: the ontology pack extends core and redeclares no core term."""

from __future__ import annotations

import re
from pathlib import Path

PACK = Path(__file__).parent.parent / "lean_mcp" / "ontology" / "lean.ttl"
# Core local names the pack must not declare again.
CORE_TERMS = {"concept", "module", "dependson", "partof", "declaration"} - {
    "declaration"
}


def blocks() -> list[tuple[str, str]]:
    text = PACK.read_text()
    text = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )
    return [
        (m.group(1), m.group(2))
        for m in re.finditer(r"^:(\w+) a (owl:\w+) ;", text, re.MULTILINE)
    ]


# spec: CONN-LEAN-MCP-R003
def test_pack_extends_core_and_redeclares_nothing():
    text = PACK.read_text()
    assert "owl:imports" not in text
    declared = blocks()
    names = {name for name, _ in declared}
    assert {
        "Declaration",
        "Theorem",
        "Definition",
        "Structure",
        "Instance",
        "LeanModule",
        "leanDependsOn",
        "declaredIn",
    } == names
    assert not {n.lower() for n in names} & CORE_TERMS
    for name, kind in declared:
        body = text.split(f":{name} a ", 1)[1].split(" .\n", 1)[0]
        parent = "rdfs:subClassOf" if kind == "owl:Class" else "rdfs:subPropertyOf"
        assert parent in body, name
    assert "core:Concept" in text and "core:Module" in text
    assert "core:dependsOn" in text and "core:partOf" in text
