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


# spec: CONN-LEAN-MCP-R003
def test_every_class_reaches_both_parent_catalogs():
    """Arbora onboarding refuses a class with no path to the engine's parent catalog.

    An engine serving the organization base finds ``core:``; one still serving the
    shared namespace finds ``kg:``. Each root names both, so every class reaches both.
    """
    text = "\n".join(
        line
        for line in PACK.read_text().splitlines()
        if not line.lstrip().startswith("#")
    )
    parents: dict[str, set[str]] = {}
    for name, body in re.findall(r"^:(\w+) a owl:Class ;(.*?) \.\n", text, re.M | re.S):
        clause = re.search(r"rdfs:subClassOf\s+([^;]+)", body)
        parents[name] = (
            set(re.findall(r"[\w]*:\w+", clause.group(1))) if clause else set()
        )
    assert len(parents) == 6

    def reaches(cls: str, prefix: str) -> bool:
        stack, seen = [cls], set()
        while stack:
            node = stack.pop()
            for parent in parents.get(node, ()):
                if parent.startswith(prefix):
                    return True
                if parent.startswith(":") and parent[1:] not in seen:
                    seen.add(parent[1:])
                    stack.append(parent[1:])
        return False

    for cls in parents:
        assert reaches(cls, "core:"), cls
        assert reaches(cls, "kg:"), cls
