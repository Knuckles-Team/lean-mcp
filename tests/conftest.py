"""Shared fixtures: a fake runner that answers `lake` calls from a script."""

from __future__ import annotations

from pathlib import Path

import pytest

from lean_mcp.api_client import Api
from lean_mcp.runner import Completed, LeanRunner

VERSION_OUT = "Lean (version 4.15.0, x86_64-unknown-linux-gnu, commit abc, Release)\n"


class FakeRunner(LeanRunner):
    """Answers each `lake` call by its argument vector; records the calls."""

    def __init__(self, root: Path, replies: dict[tuple[str, ...], Completed]) -> None:
        super().__init__(root)
        self.replies = replies
        self.calls: list[list[str]] = []

    def run(self, args: list[str], cwd: Path) -> Completed:
        self.calls.append(args)
        for key, reply in self.replies.items():
            if tuple(args[: len(key)]) == key:
                return reply
        return Completed(0, "", "")


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "proj"
    root.mkdir()
    (root / "lakefile.toml").write_text('name = "proj"\n')
    (root / "lean-toolchain").write_text("leanprover/lean4:v4.15.0\n")
    (root / "Proj.lean").write_text("theorem t : 1 = 1 := rfl\n")
    return root


def make_api(
    project: Path, replies: dict[tuple[str, ...], Completed]
) -> tuple[Api, FakeRunner]:
    runner = FakeRunner(project.parent, replies)
    return Api(runner), runner


def info(text: str) -> str:
    """One `lean --json` information line."""
    import json

    return json.dumps({"severity": "information", "data": text}) + "\n"
