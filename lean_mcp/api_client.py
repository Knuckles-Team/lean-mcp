"""The Lean operations. The SDK serves one MCP tool per public method.

Each method wraps the `lake` command line in a subprocess (see `runner.py`).
Neither method changes anything outside the project's own build directory.
"""

from __future__ import annotations

import tempfile
from importlib import resources
from pathlib import Path
from typing import Any

from .receipt import (
    SORRY_WARNING,
    build_receipt,
    digest_of,
    json_messages,
    lean_sources,
    module_of,
    parse_axioms,
    valid_name,
)
from .runner import LeanRefusal, LeanRunner

MAX_AUDIT = 2000


class Api:
    """One method per Lean operation."""

    def __init__(self, runner: LeanRunner) -> None:
        self._runner = runner

    def check(
        self,
        project_dir: str,
        file: str = "",
        declaration: str = "",
        build: bool = True,
    ) -> dict[str, Any]:
        """GET /check: check a project, a file or one declaration and return the proof receipt.

        `file` is relative to the project. `declaration` needs `file`. The receipt
        fails on `sorry` and lists every axiom `#print axioms` reports.
        """
        project = self._runner.project(project_dir)
        version = self._runner.toolchain_version(project)
        if declaration and not file:
            raise LeanRefusal(
                "DECLARATION_NEEDS_FILE", "name the file that holds the declaration"
            )
        if declaration and not valid_name(declaration):
            raise LeanRefusal(
                "DECLARATION_INVALID", "the declaration is not a plain name"
            )
        sources = self._sources(project, file)
        modules = [module_of(project, path) for path in sources] if file else []
        build_args = ["build", *modules]
        passed, has_sorry = True, False
        if build:
            done = self._runner.run(build_args, project)
            passed = done.returncode == 0
            has_sorry = SORRY_WARNING in done.stdout + done.stderr
        names = [declaration] if declaration else self._theorems(project, modules)
        axioms: list[str] = []
        if passed and names:
            found = self._audit(project, modules or self._all_modules(project), names)
            missing = [name for name in names if name not in found]
            passed = not missing
            for listed in found.values():
                axioms.extend(listed)
        has_sorry = has_sorry or "sorryAx" in axioms
        label = declaration or (modules[0] if file else project.name)
        return build_receipt(
            toolchain_version=version,
            declaration=label,
            artifact_digest=digest_of(project, sources),
            axioms=axioms,
            has_sorry=has_sorry,
            passed=passed,
        )

    def extract(self, project_dir: str, build: bool = True) -> dict[str, Any]:
        """GET /extract: list declarations and dependency edges of a project, read by Lean itself."""
        project = self._runner.project(project_dir)
        version = self._runner.toolchain_version(project)
        if build:
            done = self._runner.run(["build"], project)
            if done.returncode != 0:
                raise LeanRefusal("BUILD_FAILED", "the project does not build")
        modules = self._all_modules(project)
        records = self._extract(project, modules)
        declarations = sorted(
            (
                {k: r[k] for k in ("name", "kind", "module")}
                for r in records
                if r.get("t") == "decl"
            ),
            key=lambda d: d["name"],
        )
        edges = sorted(
            (
                {"from": r["name"], "to": dep, "predicate": "dependsOn"}
                for r in records
                if r.get("t") == "decl"
                for dep in r.get("deps", [])
            ),
            key=lambda e: (e["from"], e["to"]),
        )
        module_edges = sorted(
            (
                {"from": r["name"], "to": dep}
                for r in records
                if r.get("t") == "module"
                for dep in r.get("imports", [])
                if dep in modules
            ),
            key=lambda e: (e["from"], e["to"]),
        )
        return {
            "toolchain_version": version,
            "modules": modules,
            "declarations": declarations,
            "edges": edges,
            "module_edges": module_edges,
        }

    def _sources(self, project: Path, file: str) -> list[Path]:
        if not file:
            return lean_sources(project)
        path = (project / file).resolve()
        if project not in path.parents or path.suffix != ".lean":
            raise LeanRefusal(
                "PATH_OUTSIDE_WORKSPACE",
                "the file is not a .lean file inside the project",
            )
        if not path.is_file():
            raise LeanRefusal("FILE_NOT_FOUND", "the file does not exist")
        return [path]

    def _all_modules(self, project: Path) -> list[str]:
        return sorted(module_of(project, path) for path in lean_sources(project))

    def _extract(self, project: Path, modules: list[str]) -> list[dict[str, Any]]:
        script = (
            resources.files("lean_mcp")
            .joinpath("lean/Extract.lean")
            .read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Extract.lean"
            path.write_text(script, encoding="utf-8")
            done = self._runner.run(
                ["env", "lean", "--run", str(path), *modules], project
            )
        if done.returncode != 0:
            raise LeanRefusal(
                "EXTRACT_FAILED",
                done.stderr.strip()[:500] or "the extraction script failed",
            )
        return [value for value in json_messages(done.stdout) if "t" in value]

    def _theorems(self, project: Path, modules: list[str]) -> list[str]:
        records = self._extract(project, modules or self._all_modules(project))
        names = sorted(
            r["name"]
            for r in records
            if r.get("t") == "decl" and r.get("kind") == "theorem"
        )
        if len(names) > MAX_AUDIT:
            raise LeanRefusal(
                "TOO_MANY_DECLARATIONS",
                f"more than {MAX_AUDIT} theorems; check a file or a declaration",
            )
        return names

    def _audit(
        self, project: Path, modules: list[str], names: list[str]
    ) -> dict[str, list[str]]:
        """Run `#print axioms` for each name in one file that imports `modules`."""
        lines = [f"import {module}" for module in modules] + [
            f"#print axioms {name}" for name in names
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Audit.lean"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            done = self._runner.run(["env", "lean", "--json", str(path)], project)
        text = "\n".join(str(m.get("data", "")) for m in json_messages(done.stdout))
        return parse_axioms(text)
