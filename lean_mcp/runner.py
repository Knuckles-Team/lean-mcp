"""The one place the connector starts a Lean process.

Every `lean` and `lake` call is a subprocess with no shell, a minimal
environment, a working directory inside the workspace root and a timeout.
Project code (a lakefile, a macro, a tactic) runs only inside that subprocess.
"""

from __future__ import annotations

import os
import re
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TIMEOUT_S = 600
_PASS_ENV = ("PATH", "HOME", "ELAN_HOME", "LANG", "TMPDIR")
_VERSION = re.compile(r"\(version ([^,)\s]+)")
_PIN = re.compile(r":v?([0-9][^\s]*)\s*$")


class LeanRefusal(Exception):
    """A typed refusal. The message starts with the stable code."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class Completed:
    """One finished subprocess."""

    returncode: int
    stdout: str
    stderr: str


class LeanRunner:
    """Runs `lean` and `lake` for one workspace root."""

    def __init__(
        self,
        root: Path,
        timeout_s: int = DEFAULT_TIMEOUT_S,
        lake: str = "lake",
        pinned: str = "",
    ) -> None:
        self.root = root.resolve()
        self.timeout_s = timeout_s
        self.lake = lake
        self.pinned = pinned

    @classmethod
    def from_env(cls) -> LeanRunner:
        """Build the runner from `LEAN_WORKSPACE_ROOT`, `LEAN_TIMEOUT_S`, `LAKE_BIN` and `LEAN_TOOLCHAIN`."""
        root = os.environ.get("LEAN_WORKSPACE_ROOT", "")
        if not root:
            raise LeanRefusal(
                "WORKSPACE_UNSET",
                "set LEAN_WORKSPACE_ROOT to the directory that holds the projects",
            )
        return cls(
            Path(root),
            int(os.environ.get("LEAN_TIMEOUT_S", DEFAULT_TIMEOUT_S)),
            os.environ.get("LAKE_BIN", "lake"),
            os.environ.get("LEAN_TOOLCHAIN", ""),
        )

    def project(self, project_dir: str) -> Path:
        """Resolve `project_dir` inside the root and require a lakefile."""
        path = (self.root / project_dir).resolve()
        if path != self.root and self.root not in path.parents:
            raise LeanRefusal(
                "PATH_OUTSIDE_WORKSPACE", "the project is outside the workspace root"
            )
        if (
            not (path / "lakefile.lean").is_file()
            and not (path / "lakefile.toml").is_file()
        ):
            raise LeanRefusal(
                "PROJECT_NOT_FOUND", "no lakefile.lean or lakefile.toml in the project"
            )
        return path

    def run(self, args: list[str], cwd: Path) -> Completed:
        """Run `lake <args>` in `cwd`; kill the whole process group on timeout."""
        env = {key: os.environ[key] for key in _PASS_ENV if key in os.environ}
        try:
            proc = subprocess.Popen(
                [self.lake, *args],
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
        except FileNotFoundError as error:
            raise LeanRefusal(
                "TOOLCHAIN_MISSING", f"{self.lake} is not installed"
            ) from error
        try:
            out, err = proc.communicate(timeout=self.timeout_s)
        except subprocess.TimeoutExpired as error:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.communicate()
            raise LeanRefusal(
                "CHECK_TIMEOUT", f"no result within {self.timeout_s} seconds"
            ) from error
        return Completed(proc.returncode, out, err)

    def toolchain_version(self, project: Path) -> str:
        """The installed Lean version for `project`, refused when it differs from the pin."""
        done = self.run(["env", "lean", "--version"], project)
        found = _VERSION.search(done.stdout)
        if done.returncode != 0 or not found:
            raise LeanRefusal("TOOLCHAIN_MISSING", "lean did not report a version")
        version = found.group(1)
        pin = self.pinned or _pin_of(project)
        if pin and pin != version:
            raise LeanRefusal(
                "TOOLCHAIN_MISMATCH", f"pinned {pin}, installed {version}"
            )
        return version


def _pin_of(project: Path) -> str:
    """The version named by the project's `lean-toolchain` file, or empty."""
    pin_file = project / "lean-toolchain"
    if not pin_file.is_file():
        return ""
    found = _PIN.search(pin_file.read_text(encoding="utf-8").strip())
    return found.group(1) if found else ""
