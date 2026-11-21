---
name: lean-declaration-extraction
skill_type: skill
domain: connector
description: List the declarations and dependency edges of a Lean project with lean_extract. Use when a project must be mapped before claims are formalized.
---

# Lean declaration extraction

1. Call `lean_extract` with `project_dir`. Lean itself reads the built modules.
2. Read `declarations` (name, kind, module), `edges` (declaration uses declaration) and `module_edges` (module imports module).
3. Kinds are `theorem`, `definition`, `structure`, `inductive` and `instance`.
4. Report counts by kind, then the declarations the user asked about.

A project that does not build is refused with `BUILD_FAILED`. Fix the build first.
