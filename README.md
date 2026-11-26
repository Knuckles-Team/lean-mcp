# Lean Mcp
## CLI or API | MCP

![PyPI - Version](https://img.shields.io/pypi/v/lean-mcp)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/lean-mcp)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/lean-mcp)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/lean-mcp)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/lean-mcp)
![PyPI - License](https://img.shields.io/pypi/l/lean-mcp)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/lean-mcp)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/lean-mcp)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/lean-mcp)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/lean-mcp)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/lean-mcp)
![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/lean-mcp)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/lean-mcp)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/lean-mcp)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/lean-mcp)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/lean-mcp)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/lean-mcp)

> **Documentation** — Installation, deployment, and usage are maintained in the
> [official documentation](https://knuckles-team.github.io/lean-mcp/).

---

## Overview

**Lean Mcp** is a Model Context Protocol (MCP) server for the [Lean](https://lean-lang.org) theorem prover. It checks a Lean project, file or declaration against the pinned toolchain and returns a proof receipt, and it extracts declarations and dependency edges read by Lean itself. Built on the shared connector SDK (`scion-sdk`).

---

## Key Features

- **Proof receipts:** `checker_id`, `toolchain_version`, `declaration`, `artifact_digest`, `axioms`, `has_sorry` and `verdict`; a `sorry` fails the receipt and axioms come from `#print axioms`.
- **Declaration extraction:** theorems, definitions, structures, inductives and instances, their dependency edges and the module imports, read by Lean itself.
- **Bounded execution:** project code runs only inside a bounded subprocess with a per-call time limit, and every project path must resolve inside the workspace root.
- **Packaged content:** skills, operator and verifier prompts, and an ontology pack ship in the package.

---

## MCP

### Available MCP Tools

| MCP Tool | Description |
|----------|-------------|
| `lean_check` | Checks a project, a file or one declaration against the pinned toolchain. Returns a proof receipt: `checker_id`, `toolchain_version`, `declaration`, `artifact_digest`, `axioms`, `has_sorry`, `verdict`. A `sorry` fails the receipt. Axioms come from `#print axioms`. |
| `lean_extract` | Lists the declarations (theorem, definition, structure, inductive, instance), their dependency edges and the module imports of a project, read by Lean itself. |

### MCP Configuration Examples

#### stdio Transport (local IDEs: Cursor, Claude Desktop, VS Code)

```json
{
  "mcpServers": {
    "lean-mcp": {
      "command": "uvx",
      "args": ["--from", "lean-mcp", "lean-mcp"],
      "env": {"LEAN_WORKSPACE_ROOT": "/path/to/lean/projects"}
    }
  }
}
```

#### Streamable-HTTP Transport (networked / production)

```sh
LEAN_WORKSPACE_ROOT=/workspace lean-mcp --transport streamable-http --port 8000
```

---

## Environment Variables

| Variable | Meaning |
|---|---|
| `LEAN_WORKSPACE_ROOT` | Required. Every project path must resolve inside it. |
| `LEAN_TIMEOUT_S` | Per-call time limit in seconds. Default 600. |
| `LAKE_BIN` | The `lake` executable. Default `lake`. |
| `LEAN_TOOLCHAIN` | Optional pinned Lean version. Default: the project's `lean-toolchain` file. |

---

## Installation

```sh
pip install lean-mcp
```

Install the Lean toolchain with `elan` on the host that runs the connector. Project code runs only inside the bounded subprocess.

---

## Documentation

Specs live under `specs/`; skills, prompts and the ontology ship in the `lean_mcp` package.

## Repository Owners

Maintained by the Knuckles Team.

## Contribute

Open an issue or a pull request on [GitHub](https://github.com/Knuckles-Team/lean-mcp). Every change carries a `Spec:` trailer; see `AGENTS.md`.
