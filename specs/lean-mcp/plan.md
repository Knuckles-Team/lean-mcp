# CONN-LEAN-MCP — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

`lean_mcp` wraps the `lake` command line in bounded subprocesses and serves two tools: `lean_check` and `lean_extract`.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12); Lean 4 as an external toolchain
- **Primary Dependencies**: scion-sdk
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest with a mocked runner; one real toolchain test that skips without `lake`
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per operation; every process is a bounded subprocess
- **Scale/Scope**: 4 rows

## Constitution Check

- One owner per concept: pass. The engine owns standing; the connector owns the checker calls.
- Connectors depend on the SDK only: pass.
- No ratchets: pass.

## Project Structure

```text
lean_mcp/api_client.py  runner.py  receipt.py  lean/Extract.lean  ontology/lean.ttl
tests/  fixtures/tiny  fixtures/tiny_sorry
```

## Phase 0: Research

No unknowns. Each row names the code it touches.

## Phase 1: Design

- **Owner:** this connector owns the checker calls and the receipt mapping. The knowledge engine owns standing.
- **Cohesion:** one file starts processes (`runner.py`), one parses output (`receipt.py`), one holds the operations (`api_client.py`).
- **Dependency direction:** the connector depends on the SDK only. It never calls the engine.
- **Interface depth:** two tools hide the build, the audit and the digest behind one call each.
- **Special cases:** a declaration check audits one name; a file or project check audits every theorem found by extraction.
- **State:** none. Each call is stateless; the only writes are the project's own build directory.
- **Environment:** `LEAN_WORKSPACE_ROOT`, `LEAN_TIMEOUT_S`, `LAKE_BIN` and `LEAN_TOOLCHAIN`; the toolchain is installed on the run host only.

### Architecture

`lean_mcp/api_client.py` holds one method per operation: `check` and `extract`. `lean_mcp/runner.py` is the only code that starts a process. It runs `lake` with no shell, a minimal environment, a working directory inside `LEAN_WORKSPACE_ROOT` and a timeout. `lean_mcp/receipt.py` parses Lean output and builds the receipt. `lean_mcp/auth.py` builds the client. The SDK `Connector` serves one tool per method.

### Interfaces

Entry point `scion_sdk.connector`: `lean-mcp = "lean_mcp:connector"`.

Settings: `LEAN_WORKSPACE_ROOT` (required), `LEAN_TIMEOUT_S` (default 600), `LAKE_BIN` (default `lake`), `LEAN_TOOLCHAIN` (optional pin; the project's `lean-toolchain` file is the default pin).

Receipt: `checker_id` is `lean4`. `artifact_digest` is the SHA-256 of the checked sources and the pin files. `axioms` is the sorted union of `#print axioms` output. `verdict` is `pass` only for a clean build with no `sorry`.

## Production caller chain

MCP tool `lean_check` → `lean_mcp/api_client.py::Api.check` → `lean_mcp/runner.py::LeanRunner.toolchain_version`, `LeanRunner.run` (`lake build`, `lake env lean --json`) → `lean_mcp/receipt.py::build_receipt`.

MCP tool `lean_extract` → `Api.extract` → `Api._extract` → `LeanRunner.run` (`lake env lean --run lean/Extract.lean`).


## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `ruff-format`, `connector-standard`, `secrets`, `tests-fast`. Each row names its proving test. No suppression and no duplicate implementation.

## Cross-repo seams

- The receipt is recorded in the knowledge engine as evidence through its claim surface: `contracts/receipt.md` (`CONN-LEAN-MCP-R001`). The engine owns standing and the `formalizes` edge. This connector never writes to the engine.
