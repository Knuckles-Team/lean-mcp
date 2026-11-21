# CONN-LEAN-MCP — Test specification

| Test ID | Requirement | Proving test |
|---|---|---|
| T-001 | `CONN-LEAN-MCP-R001` | `tests/test_check.py::test_a_clean_proof_passes_with_standard_axioms` |
| T-002 | `CONN-LEAN-MCP-R001` | `tests/test_check.py::test_sorry_fails_the_receipt` |
| T-003 | `CONN-LEAN-MCP-R001` | `tests/test_check.py::test_nonstandard_axioms_are_reported` |
| T-004 | `CONN-LEAN-MCP-R001` | `tests/test_check.py::test_toolchain_mismatch_is_refused` |
| T-005 | `CONN-LEAN-MCP-R001` | `tests/test_runner.py::test_a_timeout_kills_the_process_and_refuses` |
| T-006 | `CONN-LEAN-MCP-R002` | `tests/test_extract.py::test_extract_returns_declarations_and_edges` |
| T-007 | `CONN-LEAN-MCP-R002` | `tests/test_extract.py::test_a_failed_build_is_refused` |
| T-008 | `CONN-LEAN-MCP-R003` | `tests/test_pack.py::test_pack_extends_core_and_redeclares_nothing` |
| T-009 | `CONN-LEAN-MCP-R004` | `tests/test_surface.py::test_every_tool_has_a_contract_a_prompt_and_a_skill` |
