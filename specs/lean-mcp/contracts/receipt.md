# Receipt contract (CONN-LEAN-MCP-R001)

Provider: lean-mcp CONN-LEAN-MCP-R001
Consumer: medulla MEDULLA-DECISION-ENGINE-R652.10

## Wire shape

The receipt that `lean_check` returns has seven fields. The knowledge engine records it as proof evidence on a claim.

| Field | Type | Meaning |
|---|---|---|
| `checker_id` | string | `lean4` |
| `toolchain_version` | string | The installed Lean version |
| `declaration` | string | The declaration, the module, or the project name |
| `artifact_digest` | string | SHA-256 of the checked sources and pin files, 64 lower-case hex characters |
| `axioms` | list of string | Sorted axioms that `#print axioms` reports |
| `has_sorry` | boolean | True when a proof holds an unfinished step |
| `verdict` | string | `pass` or `fail` |

## Refusal codes

`PROJECT_NOT_FOUND`, `PATH_OUTSIDE_WORKSPACE`, `TOOLCHAIN_MISMATCH`, `TOOLCHAIN_MISSING`, `CHECK_TIMEOUT`, `DECLARATION_NEEDS_FILE`, `DECLARATION_INVALID`, `FILE_NOT_FOUND`, `TOO_MANY_DECLARATIONS`. A refusal returns no receipt.
