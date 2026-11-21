---
name: lean-proof-checking
skill_type: skill
domain: connector
description: Check a Lean file, project or declaration with lean_check and read the proof receipt. Use when a statement must be machine-checked before it is trusted.
---

# Lean proof checking

1. Pick the scope. Pass `project_dir` alone for a project, add `file` for one file, add `declaration` for one declaration.
2. Call `lean_check`. It runs the pinned toolchain in a subprocess with a time limit.
3. Read the receipt: `checker_id`, `toolchain_version`, `declaration`, `artifact_digest`, `axioms`, `has_sorry` and `verdict`.
4. Treat `verdict: fail` as unproven. A `sorry` always fails. Report any axiom outside `propext`, `Classical.choice` and `Quot.sound` as nonstandard.
5. Hand the receipt on unchanged. Never edit a receipt field.

Refusals carry a stable code such as `TOOLCHAIN_MISMATCH` or `CHECK_TIMEOUT`. Report the code and stop.
