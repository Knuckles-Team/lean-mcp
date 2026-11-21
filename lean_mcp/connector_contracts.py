"""What the Lean surface declares: tool use, links, data locations and roles.

The SDK serves these as the `ontology://` contracts resource and answers "how
do I do task X" from them. Every tool is called by a step and named by a link.
"""

from scion_sdk.surface_contracts import (
    BusinessRole,
    DataLocation,
    Refusal,
    SurfaceLink,
    ToolStep,
    ToolUseContract,
)

_RECEIPT = (
    "checker_id",
    "toolchain_version",
    "declaration",
    "artifact_digest",
    "axioms",
    "has_sorry",
    "verdict",
)
_COMMON = (
    Refusal("PROJECT_NOT_FOUND", "the project has no lakefile"),
    Refusal("PATH_OUTSIDE_WORKSPACE", "the path leaves the workspace root"),
    Refusal(
        "TOOLCHAIN_MISMATCH", "the installed toolchain differs from the pinned one"
    ),
    Refusal("TOOLCHAIN_MISSING", "lean or lake is not installed"),
    Refusal("CHECK_TIMEOUT", "the run exceeded its time limit"),
)

CONTRACTS = (
    ToolUseContract(
        "check-proof",
        (
            ToolStep(
                "lean_check",
                params=("project_dir", "file", "declaration", "build"),
                result=_RECEIPT,
                refusals=(
                    *_COMMON,
                    Refusal(
                        "DECLARATION_NEEDS_FILE",
                        "a declaration needs the file that holds it",
                    ),
                    Refusal(
                        "DECLARATION_INVALID", "the declaration is not a plain name"
                    ),
                    Refusal("FILE_NOT_FOUND", "the file does not exist"),
                    Refusal(
                        "TOO_MANY_DECLARATIONS",
                        "the scope holds too many theorems to audit",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "extract-declarations",
        (
            ToolStep(
                "lean_extract",
                params=("project_dir", "build"),
                result=(
                    "toolchain_version",
                    "modules",
                    "declarations",
                    "edges",
                    "module_edges",
                ),
                refusals=(
                    *_COMMON,
                    Refusal("BUILD_FAILED", "the project does not build"),
                    Refusal("EXTRACT_FAILED", "the extraction script failed"),
                ),
            ),
        ),
    ),
)
LINKS = (
    SurfaceLink(
        "check-proof",
        tools=("lean_check",),
        prompts=("lean-operator", "lean-verifier"),
        skills=("lean-proof-checking",),
    ),
    SurfaceLink(
        "extract-declarations",
        tools=("lean_extract",),
        prompts=("lean-operator", "lean-verifier"),
        skills=("lean-declaration-extraction",),
    ),
)
LOCATIONS = (
    DataLocation(
        "lean_declarations",
        ("LeanDeclaration",),
        "LEAN_WORKSPACE_ROOT",
        "lean_extract",
        federation_key="name",
    ),
)
ROLES = (BusinessRole("verifier", tasks=("check-proof", "extract-declarations")),)
