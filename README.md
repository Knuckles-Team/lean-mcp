# lean-mcp

MCP connector for the [Lean](https://lean-lang.org) theorem prover.

| Tool | What it does |
|---|---|
| `lean_check` | Checks a project, a file or one declaration against the pinned toolchain. Returns a proof receipt: `checker_id`, `toolchain_version`, `declaration`, `artifact_digest`, `axioms`, `has_sorry`, `verdict`. A `sorry` fails the receipt. Axioms come from `#print axioms`. |
| `lean_extract` | Lists the declarations (theorem, definition, structure, inductive, instance), their dependency edges and the module imports of a project, read by Lean itself. |

## Settings

| Variable | Meaning |
|---|---|
| `LEAN_WORKSPACE_ROOT` | Required. Every project path must resolve inside it. |
| `LEAN_TIMEOUT_S` | Per-call time limit in seconds. Default 600. |
| `LAKE_BIN` | The `lake` executable. Default `lake`. |
| `LEAN_TOOLCHAIN` | Optional pinned Lean version. Default: the project's `lean-toolchain` file. |

Install the Lean toolchain with `elan` on the host that runs the connector. Project code runs only inside the bounded subprocess.
