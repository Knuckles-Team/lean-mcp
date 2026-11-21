# CONN-LEAN-MCP — Lean connector

Component: Lean connector

Owner: lean-mcp.

Depends-on: [Machine-checked proof evidence](https://github.com/Knuckles-Team/medulla/blob/main/specs/decision-engine/requirements.md)

## Purpose and user stories

The connector checks Lean proofs against a pinned toolchain and returns a typed proof receipt. It extracts declarations and dependency edges from a Lean project. It ships an ontology pack that extends the core ontology only.

## Why a new spec

The specs of this repository were read; none owns the Lean operations. The search `git grep -n "lean" -- specs` found nothing before this spec.

## Scope and interfaces

In scope: the `lean` and `lake` calls, the receipt mapping, the declaration extraction, the ontology pack, and the prompts, skills and tool-use contracts of each tool. Out of scope: claim standing, evidence storage and the `formalizes` edge, which the knowledge engine owns. Server start, version files, container files and gates, which the SDK and pipelines own.

## User Scenarios & Testing

### User Story 1 - An agent machine-checks a statement (Priority: P1)

An agent holds a formal statement and needs a receipt that a checker accepted it, so that the receipt can be recorded as evidence.

**Acceptance Scenarios**:

1. **Given** a project with a finished proof, **When** the agent calls `lean_check` for the declaration, **Then** the receipt has verdict `pass`, `has_sorry` false and the axioms that `#print axioms` lists.
2. **Given** a proof with `sorry`, **When** the agent calls `lean_check`, **Then** the receipt has `has_sorry` true and verdict `fail`.
3. **Given** a project, **When** the agent calls `lean_extract`, **Then** it receives declarations, dependency edges and module imports.

### Edge Cases

- A toolchain other than the pin is refused with `TOOLCHAIN_MISMATCH`.
- A run past the time limit is killed and refused with `CHECK_TIMEOUT`.
- A path outside the workspace root is refused with `PATH_OUTSIDE_WORKSPACE`.

## Requirements

- **FR-001**: Check. Rows: `CONN-LEAN-MCP-R001`.
- **FR-002**: Extract. Rows: `CONN-LEAN-MCP-R002`.
- **FR-003**: Pack. Rows: `CONN-LEAN-MCP-R003`.
- **FR-004**: Surfaces. Rows: `CONN-LEAN-MCP-R004`.

## Success Criteria

- **SC-001**: A finished proof returns verdict `pass`; a `sorry` returns verdict `fail`. Rows: `CONN-LEAN-MCP-R001`.
- **SC-002**: The pack declares no term that core declares. Rows: `CONN-LEAN-MCP-R003`.

## Assumptions

- The Lean toolchain is installed on the host that runs the connector.
- A project keeps its sources at the project root, so a file path maps to a module name.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-LEAN-MCP-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-LEAN-MCP-R002` | [plan.md](plan.md) | T-006 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-LEAN-MCP-R003` | [plan.md](plan.md) | T-008 | [test-spec.md](test-spec.md) |
| FR-004 | `CONN-LEAN-MCP-R004` | [plan.md](plan.md) | T-009 | [test-spec.md](test-spec.md) |
