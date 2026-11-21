"""R004: each tool carries its contract, prompt and skill."""

from __future__ import annotations

import json
from pathlib import Path

from lean_mcp.api_client import Api
from lean_mcp.connector_contracts import CONTRACTS, LINKS

ROOT = Path(__file__).parent.parent / "lean_mcp"


def tools() -> set[str]:
    return {f"lean_{name}" for name in dir(Api) if not name.startswith("_")}


# spec: CONN-LEAN-MCP-R004
def test_every_tool_has_a_contract_a_prompt_and_a_skill():
    served = tools()
    assert served == {"lean_check", "lean_extract"}
    contracted = {step.tool for contract in CONTRACTS for step in contract.steps}
    linked = {tool for link in LINKS for tool in link.tools}
    assert served == contracted == linked
    prompts = {
        p.stem: json.loads(p.read_text()) for p in (ROOT / "prompts").glob("*.json")
    }
    for tool in served:
        assert any(tool in doc["agent"]["tools"] for doc in prompts.values()), tool
    skills = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
    for link in LINKS:
        assert set(link.skills) <= skills
        assert set(link.prompts) <= set(prompts)
