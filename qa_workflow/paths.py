"""
Single source of truth for QA workflow output locations.

Every agent and script MUST obtain output paths from this module. No agent may
construct an `outputs/...` path by string concatenation. Before this module
existed, nine agent files invented their own locations and disagreed with each
other (`Test_Cases.xlsx` vs `Test_Cases_PBI_<PBI>.xlsx`, `.md` vs `.docx`,
screenshots in three different places), which is what produced the flat,
cluttered PBI folders this replaces.

Standard structure, created automatically for every PBI run:

    outputs/<PBI>/
    ├── deliverables/     final, user-facing QA output
    ├── working/          intermediate artifacts the workflow needs but users don't
    └── logs/             summaries, validation reports, debug/history

Type-conditional subdirectories are created ONLY when the corresponding type is
in `selected_types`. This mirrors the fail-closed behaviour of the UI and DB
agents: no UI selected means no UI directory, so there is nowhere for stray UI
artifacts to land.

    deliverables/ui/screenshots/   only when "UI" in selected_types
    deliverables/db/               only when "Database" in selected_types

This module contains no QA business logic and does not decide scope. It reads
`selected_types`; it never writes it.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# The canonical type vocabulary. Mirrors the agent specifications. Categories
# (Security, Performance, ErrorHandling, Boundary) are NOT types and never
# appear here.
SUPPORTED_TYPES = ("API", "UI", "Database", "BusinessLogic", "Integration")

# Root of the outputs tree, overridable for tests and dry runs.
DEFAULT_OUTPUT_ROOT = os.environ.get("QA_OUTPUT_ROOT", "outputs")

# Bucket names, exported so callers never hardcode the strings.
DELIVERABLES = "deliverables"
WORKING = "working"
LOGS = "logs"


class OutputPaths:
    """
    Resolves every output location for a single PBI run.

    Usage:

        paths = OutputPaths("643243", selected_types=["API"])
        paths.ensure()                      # create the directory structure
        paths.user_context                  # outputs/643243/working/user-context.json
        paths.qa_understanding_document     # outputs/643243/deliverables/...docx

    `selected_types` may be omitted when only generic paths are needed, but
    `ensure()` will then skip the type-conditional directories.
    """

    def __init__(self, pbi_number, selected_types=None, output_root=None):
        self.pbi_number = str(pbi_number)
        self.output_root = Path(output_root or DEFAULT_OUTPUT_ROOT)
        self.selected_types = list(selected_types) if selected_types else []

        unsupported = [t for t in self.selected_types if t not in SUPPORTED_TYPES]
        if unsupported:
            raise ValueError(
                f"Unsupported type(s) {unsupported}. Legal values: {list(SUPPORTED_TYPES)}. "
                f"Security/Performance/ErrorHandling/Boundary are Categories, not types."
            )

    # ---------------------------------------------------------------- roots
    @property
    def base(self) -> Path:
        return self.output_root / self.pbi_number

    @property
    def deliverables(self) -> Path:
        return self.base / DELIVERABLES

    @property
    def working(self) -> Path:
        return self.base / WORKING

    @property
    def logs(self) -> Path:
        return self.base / LOGS

    # -------------------------------------------------- working artifacts
    # Internal to the workflow. Users normally never open these.
    @property
    def user_context(self) -> Path:
        """The authoritative scope contract."""
        return self.working / "user-context.json"

    @property
    def pbi_data(self) -> Path:
        return self.working / "pbi-data.json"

    @property
    def integration_docs(self) -> Path:
        """Extraction of user-provided supporting documentation."""
        return self.working / "integration-docs.json"

    @property
    def scenarios_parsed(self) -> Path:
        return self.working / "scenarios-parsed.json"

    @property
    def qa_doc_extract(self) -> Path:
        return self.working / "qa-doc-extract.json"

    @property
    def test_cases_generated(self) -> Path:
        return self.working / "test-cases-generated.json"

    def working_file(self, filename: str) -> Path:
        """Escape hatch for one-off intermediates, incl. generated .py generators."""
        return self.working / filename

    # ---------------------------------------------- deliverable artifacts
    @property
    def qa_understanding_document(self) -> Path:
        return self.deliverables / "QA_Understanding_Document.docx"

    @property
    def test_scenarios(self) -> Path:
        return self.deliverables / "Test-Scenarios-Mapped-to-AC.xlsx"

    @property
    def test_cases(self) -> Path:
        """Canonical test case workbook. Contains the Test Type Map sheet."""
        return self.deliverables / f"Test_Cases_PBI_{self.pbi_number}.xlsx"

    def deliverable_file(self, filename: str) -> Path:
        return self.deliverables / filename

    # ------------------------------------------- type-conditional: UI
    def _require(self, type_name: str, what: str) -> None:
        if self.selected_types and type_name not in self.selected_types:
            raise ScopeViolation(
                f"{what} requested but '{type_name}' is not in selected_types "
                f"{self.selected_types}. This path must not be created."
            )

    @property
    def ui_dir(self) -> Path:
        self._require("UI", "UI output directory")
        return self.deliverables / "ui"

    @property
    def ui_screenshots(self) -> Path:
        return self.ui_dir / "screenshots"

    @property
    def ui_execution_guide(self) -> Path:
        return self.ui_dir / "UI_Test_Execution_Guide.md"

    @property
    def ui_test_results(self) -> Path:
        return self.ui_dir / "UI_Test_Results.xlsx"

    # -------------------------------------- type-conditional: Database
    @property
    def db_dir(self) -> Path:
        self._require("Database", "Database output directory")
        return self.deliverables / "db"

    @property
    def db_research_plan(self) -> Path:
        return self.db_dir / "db-research-plan.json"

    @property
    def db_analysis(self) -> Path:
        return self.db_dir / "DB_Analysis.md"

    # ------------------------------------------------------------- logs
    @property
    def workflow_summary(self) -> Path:
        return self.logs / "00-WORKFLOW-SUMMARY.md"

    def phase_report(self, phase: int, name: str) -> Path:
        slug = name.strip().lower().replace(" ", "-").replace("_", "-")
        return self.logs / f"phase{phase}-{slug}.md"

    def log_file(self, filename: str) -> Path:
        return self.logs / filename

    # -------------------------------------------------------- lifecycle
    def ensure(self) -> "OutputPaths":
        """
        Create the standard structure. Idempotent — safe to call at the start of
        every phase, so a resumed or partial run self-heals.

        Type-conditional directories are created only for selected types.
        """
        for d in (self.base, self.deliverables, self.working, self.logs):
            d.mkdir(parents=True, exist_ok=True)

        if "UI" in self.selected_types:
            self.ui_screenshots.mkdir(parents=True, exist_ok=True)
        if "Database" in self.selected_types:
            self.db_dir.mkdir(parents=True, exist_ok=True)

        return self

    # --------------------------------------------------------- helpers
    @classmethod
    def from_context(cls, pbi_number, output_root=None) -> "OutputPaths":
        """
        Build from an existing user-context.json, so agents in later phases pick
        up `selected_types` without re-deriving scope.

        Falls back to the legacy flat location if the contract has not yet been
        migrated, so this works mid-migration.
        """
        probe = cls(pbi_number, output_root=output_root)
        candidates = [probe.user_context, probe.base / "user-context.json"]

        for candidate in candidates:
            if candidate.is_file():
                ctx = json.loads(candidate.read_text(encoding="utf-8"))
                return cls(
                    pbi_number,
                    selected_types=ctx.get("selected_types") or [],
                    output_root=output_root,
                )

        raise FileNotFoundError(
            f"No user-context.json for PBI {pbi_number}. Looked in: "
            + ", ".join(str(c) for c in candidates)
            + ". Run Phase 1 first."
        )

    def describe(self) -> str:
        """Human-readable tree. Used by the dry-run validator."""
        lines = [f"{self.base}/"]
        lines.append(f"├── {DELIVERABLES}/")
        lines.append(f"│   ├── {self.qa_understanding_document.name}")
        lines.append(f"│   ├── {self.test_scenarios.name}")
        lines.append(f"│   ├── {self.test_cases.name}")
        if "UI" in self.selected_types:
            lines.append("│   ├── ui/")
            lines.append("│   │   ├── screenshots/")
            lines.append(f"│   │   ├── {self.ui_execution_guide.name}")
            lines.append(f"│   │   └── {self.ui_test_results.name}")
        if "Database" in self.selected_types:
            lines.append("│   └── db/")
            lines.append(f"│       ├── {self.db_research_plan.name}")
            lines.append(f"│       └── {self.db_analysis.name}")
        lines.append(f"├── {WORKING}/")
        for p in (self.user_context, self.pbi_data, self.integration_docs):
            lines.append(f"│   ├── {p.name}")
        lines.append("│   └── (intermediate json + generated scripts)")
        lines.append(f"└── {LOGS}/")
        lines.append(f"    ├── {self.workflow_summary.name}")
        lines.append("    └── (phase reports, validation, debug)")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"OutputPaths(pbi={self.pbi_number!r}, types={self.selected_types!r})"


class ScopeViolation(Exception):
    """Raised when a path is requested for a type that is not in selected_types."""
