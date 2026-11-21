"""Parse Lean output and build the proof receipt.

The receipt fields match the claim surface of the knowledge engine:
`checker_id`, `toolchain_version`, `declaration`, `artifact_digest`, `axioms`,
`has_sorry` and `verdict`.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

CHECKER_ID = "lean4"
SORRY_WARNING = "declaration uses 'sorry'"
_AXIOMS = re.compile(r"'([^']+)' depends on axioms: \[(.*?)\]", re.DOTALL)
_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.'«»]*$")
_SKIP_DIRS = {".lake", ".git", "build"}


def valid_name(name: str) -> bool:
    """Whether `name` is a plain declaration name (no whitespace, no operators)."""
    return bool(_NAME.match(name))


def parse_axioms(text: str) -> dict[str, list[str]]:
    """Map each declaration in `#print axioms` output to its sorted axiom list."""
    found: dict[str, list[str]] = {}
    for name, body in _AXIOMS.findall(text):
        found[name] = sorted(
            {
                part.strip()
                for part in body.replace("\n", " ").split(",")
                if part.strip()
            }
        )
    for name in re.findall(r"'([^']+)' does not depend on any axioms", text):
        found[name] = []
    return found


def json_messages(text: str) -> list[dict[str, Any]]:
    """The JSON message lines of `lean --json`; other lines are kept as plain messages."""
    out: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except ValueError:
            out.append({"severity": "information", "data": line})
            continue
        if isinstance(value, dict):
            out.append(value)
    return out


def module_of(project: Path, file: Path) -> str:
    """The module name of `file`, taking the project root as the source root."""
    return ".".join(file.relative_to(project).with_suffix("").parts)


def lean_sources(project: Path) -> list[Path]:
    """Every module source of the project outside build and dependency directories, sorted."""
    return sorted(
        path
        for path in project.rglob("*.lean")
        if path != project / "lakefile.lean"
        and not (_SKIP_DIRS & set(path.relative_to(project).parts))
    )


def digest_of(project: Path, files: list[Path]) -> str:
    """SHA-256 over the sorted relative paths and bytes of `files` and the project pin files."""
    pins = [
        project / name
        for name in (
            "lakefile.lean",
            "lakefile.toml",
            "lake-manifest.json",
            "lean-toolchain",
        )
    ]
    sha = hashlib.sha256()
    for path in sorted({*files, *(p for p in pins if p.is_file())}):
        sha.update(str(path.relative_to(project)).encode())
        sha.update(b"\0")
        sha.update(path.read_bytes())
        sha.update(b"\0")
    return sha.hexdigest()


def build_receipt(
    *,
    toolchain_version: str,
    declaration: str,
    artifact_digest: str,
    axioms: list[str],
    has_sorry: bool,
    passed: bool,
) -> dict[str, Any]:
    """The receipt. A `sorry` or a failed build never passes."""
    ok = passed and not has_sorry
    return {
        "checker_id": CHECKER_ID,
        "toolchain_version": toolchain_version,
        "declaration": declaration,
        "artifact_digest": artifact_digest,
        "axioms": sorted(set(axioms)),
        "has_sorry": has_sorry,
        "verdict": "pass" if ok else "fail",
    }
