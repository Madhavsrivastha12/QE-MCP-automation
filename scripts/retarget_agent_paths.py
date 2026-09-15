"""
Rewrite hardcoded outputs/ paths in the agent specifications to use
qa_workflow.paths.OutputPaths.

Before this, nine agent files each built their own `outputs/<PBI>/...` strings
and disagreed on filenames and locations. This script applies one explicit
substitution table so they all resolve paths from the same module.

Dry-run by default; --apply to write.

    python scripts/retarget_agent_paths.py
    python scripts/retarget_agent_paths.py --apply

Idempotent: substitutions that have already been applied simply do not match.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
AGENT_DIR = REPO / ".claude" / "agents"
SKILL_DIR = REPO / ".claude" / "skills"

# Python-expression substitutions. Order matters: longest/most specific first.
# {pbi} / {pbi_number} / {pbi_num} variants are all covered by the regex.
PBI_VAR = r"\{pbi(?:_number|_num)?\}"

CODE_SUBS: list[tuple[str, str]] = [
    # --- working artifacts -------------------------------------------------
    (rf"Path\(f['\"]outputs/{PBI_VAR}/user-context\.json['\"]\)", "paths.user_context"),
    (rf"Path\(f['\"]outputs/{PBI_VAR}/pbi-data\.json['\"]\)", "paths.pbi_data"),
    (rf"Path\(f['\"]outputs/{PBI_VAR}/integration-docs\.json['\"]\)", "paths.integration_docs"),
    (rf"f['\"]outputs/{PBI_VAR}/user-context\.json['\"]", "paths.user_context"),
    (rf"f['\"]outputs/{PBI_VAR}/pbi-data\.json['\"]", "paths.pbi_data"),
    (rf"f['\"]outputs/{PBI_VAR}/integration-docs\.json['\"]", "paths.integration_docs"),

    # --- deliverables ------------------------------------------------------
    (rf"Path\(f['\"]outputs/{PBI_VAR}/QA_Understanding_Document\.(?:docx|md)['\"]\)",
     "paths.qa_understanding_document"),
    (rf"f['\"]outputs/{PBI_VAR}/QA_Understanding_Document\.(?:docx|md)['\"]",
     "paths.qa_understanding_document"),
    (rf"Path\(f['\"]outputs/{PBI_VAR}/Test-Scenarios-Mapped-to-AC\.xlsx['\"]\)",
     "paths.test_scenarios"),
    (rf"f['\"]outputs/{PBI_VAR}/Test-Scenarios-Mapped-to-AC\.xlsx['\"]",
     "paths.test_scenarios"),
    (rf"Path\(f['\"]outputs/{PBI_VAR}/Test_Cases_PBI_{PBI_VAR}\.xlsx['\"]\)",
     "paths.test_cases"),
    (rf"f['\"]outputs/{PBI_VAR}/Test_Cases_PBI_{PBI_VAR}\.xlsx['\"]",
     "paths.test_cases"),
    (rf"f['\"]outputs/{PBI_VAR}/Test_Cases\.xlsx['\"]", "paths.test_cases"),

    # --- type-conditional --------------------------------------------------
    (rf"f['\"]outputs/{PBI_VAR}/screenshots/?['\"]", "paths.ui_screenshots"),
    (rf"f['\"]outputs/{PBI_VAR}/ui-test-execution-guide\.md['\"]", "paths.ui_execution_guide"),
    (rf"f['\"]outputs/{PBI_VAR}/ui-test-results\.xlsx['\"]", "paths.ui_test_results"),
    (rf"f['\"]outputs/{PBI_VAR}/db-research-plan\.json['\"]", "paths.db_research_plan"),
]

# Prose/documentation substitutions — plain text, applied literally.
PROSE_SUBS: list[tuple[str, str]] = [
    ("outputs/<PBI>/user-context.json", "outputs/<PBI>/working/user-context.json"),
    ("outputs/<PBI>/pbi-data.json", "outputs/<PBI>/working/pbi-data.json"),
    ("outputs/<PBI>/integration-docs.json", "outputs/<PBI>/working/integration-docs.json"),
    ("outputs/<PBI>/QA_Understanding_Document.docx",
     "outputs/<PBI>/deliverables/QA_Understanding_Document.docx"),
    ("outputs/<PBI>/QA_Understanding_Document.md",
     "outputs/<PBI>/deliverables/QA_Understanding_Document.docx"),
    ("outputs/<PBI>/Test-Scenarios-Mapped-to-AC.xlsx",
     "outputs/<PBI>/deliverables/Test-Scenarios-Mapped-to-AC.xlsx"),
    ("outputs/<PBI>/Test_Cases_PBI_<PBI>.xlsx",
     "outputs/<PBI>/deliverables/Test_Cases_PBI_<PBI>.xlsx"),
    ("outputs/<PBI>/Test_Cases.xlsx",
     "outputs/<PBI>/deliverables/Test_Cases_PBI_<PBI>.xlsx"),
    ("outputs/<PBI>/screenshots/", "outputs/<PBI>/deliverables/ui/screenshots/"),
    ("outputs/<PBI>/ui-test-execution-guide.md",
     "outputs/<PBI>/deliverables/ui/UI_Test_Execution_Guide.md"),
    ("outputs/<PBI>/ui-test-results.xlsx",
     "outputs/<PBI>/deliverables/ui/UI_Test_Results.xlsx"),
    ("outputs/<PBI>/db-research-plan.json",
     "outputs/<PBI>/deliverables/db/db-research-plan.json"),
    # Interpolated forms that appear inside Agent() prompt strings and prose.
    # These tell subagents where to save, so they must name the standard layout.
    ("outputs/{pbi_number}/pbi-data.json", "outputs/{pbi_number}/working/pbi-data.json"),
    ("outputs/{pbi_number}/user-context.json", "outputs/{pbi_number}/working/user-context.json"),
    ("outputs/{pbi_number}/integration-docs.json",
     "outputs/{pbi_number}/working/integration-docs.json"),
    ("outputs/{pbi_number}/QA_Understanding_Document.md",
     "outputs/{pbi_number}/deliverables/QA_Understanding_Document.docx"),
    ("outputs/{pbi_number}/QA_Understanding_Document.docx",
     "outputs/{pbi_number}/deliverables/QA_Understanding_Document.docx"),
    ("outputs/{pbi_number}/Test-Scenarios-Mapped-to-AC.xlsx",
     "outputs/{pbi_number}/deliverables/Test-Scenarios-Mapped-to-AC.xlsx"),
    ("outputs/{pbi_number}/Test_Cases_PBI_{pbi_number}.xlsx",
     "outputs/{pbi_number}/deliverables/Test_Cases_PBI_{pbi_number}.xlsx"),
    ("outputs/{pbi_number}/Test_Cases.xlsx",
     "outputs/{pbi_number}/deliverables/Test_Cases_PBI_{pbi_number}.xlsx"),
    ("outputs/{pbi_number}/ui-test-execution-guide.md",
     "outputs/{pbi_number}/deliverables/ui/UI_Test_Execution_Guide.md"),
    ("outputs/{pbi_number}/ui-test-results.xlsx",
     "outputs/{pbi_number}/deliverables/ui/UI_Test_Results.xlsx"),
    ("outputs/{pbi_number}/screenshots/", "outputs/{pbi_number}/deliverables/ui/screenshots/"),
    ("outputs/{pbi_number}/db-analysis.md", "outputs/{pbi_number}/deliverables/db/DB_Analysis.md"),
    ("outputs/{pbi_number}/db-research-plan.json",
     "outputs/{pbi_number}/deliverables/db/db-research-plan.json"),
    ("outputs/{pbi}/pbi-data.json", "outputs/{pbi}/working/pbi-data.json"),
    ("outputs/{pbi}/user-context.json", "outputs/{pbi}/working/user-context.json"),
    ("outputs/{pbi}/integration-docs.json", "outputs/{pbi}/working/integration-docs.json"),
    ("outputs/{pbi}/db-analysis.md", "outputs/{pbi}/deliverables/db/DB_Analysis.md"),
    ("outputs/{pbi}/screenshots/", "outputs/{pbi}/deliverables/ui/screenshots/"),
    ("outputs/{pbi}/ui-test-execution-guide.md",
     "outputs/{pbi}/deliverables/ui/UI_Test_Execution_Guide.md"),

    # Concrete-PBI examples used throughout the docs.
    ("outputs/643243/pbi-data.json", "outputs/643243/working/pbi-data.json"),
    ("outputs/643243/user-context.json", "outputs/643243/working/user-context.json"),
    ("outputs/643243/integration-docs.json", "outputs/643243/working/integration-docs.json"),
    ("outputs/643243/QA_Understanding_Document.docx",
     "outputs/643243/deliverables/QA_Understanding_Document.docx"),
    ("outputs/643243/Test-Scenarios-Mapped-to-AC.xlsx",
     "outputs/643243/deliverables/Test-Scenarios-Mapped-to-AC.xlsx"),
    ("outputs/643243/Test_Cases.xlsx",
     "outputs/643243/deliverables/Test_Cases_PBI_643243.xlsx"),

    # Remaining filename variants (second pass).
    ("outputs/<PBI>/ui-test-results.json",
     "outputs/<PBI>/deliverables/ui/UI_Test_Results.json"),
    ("outputs/{pbi_number}/ui-test-results.json",
     "outputs/{pbi_number}/deliverables/ui/UI_Test_Results.json"),
    ("outputs/<PBI>/db-analysis.md", "outputs/<PBI>/deliverables/db/DB_Analysis.md"),
    ("outputs/<PBI>/db-test-data-requirements.txt",
     "outputs/<PBI>/deliverables/db/db-test-data-requirements.txt"),
    ("outputs/{pbi_number}/db-test-data-requirements.txt",
     "outputs/{pbi_number}/deliverables/db/db-test-data-requirements.txt"),
    ("outputs/<PBI>/db-test-scripts.sql",
     "outputs/<PBI>/deliverables/db/db-test-scripts.sql"),
    ("outputs/{pbi_number}/db-test-scripts.sql",
     "outputs/{pbi_number}/deliverables/db/db-test-scripts.sql"),
    ("outputs/{pbi_number}/00-WORKFLOW-SUMMARY.md",
     "outputs/{pbi_number}/logs/00-WORKFLOW-SUMMARY.md"),
    ("outputs/<PBI>/00-WORKFLOW-SUMMARY.md",
     "outputs/<PBI>/logs/00-WORKFLOW-SUMMARY.md"),
]

# Multi-line ASCII "example output tree" blocks. Several agent files still show
# the old flat layout as documentation, which would teach a future run the wrong
# structure even though the code resolves paths correctly. Replaced wholesale.
CANONICAL_TREE = """outputs/643243/
├── deliverables/                           ← final, user-facing QA output
│   ├── QA_Understanding_Document.docx      ← Phase 3
│   ├── Test-Scenarios-Mapped-to-AC.xlsx    ← Phase 4
│   ├── Test_Cases_PBI_643243.xlsx          ← Phase 5
│   ├── ui/                                 ← ONLY when "UI" selected
│   └── db/                                 ← ONLY when "Database" selected
├── working/                                ← intermediate artifacts
│   ├── pbi-data.json                       ← Phase 1 (ADO data)
│   ├── user-context.json                   ← Phase 1 (scope contract)
│   └── integration-docs.json               ← Phase 2
└── logs/                                   ← phase reports, validation, debug
    └── 00-WORKFLOW-SUMMARY.md              ← Summary report
"""

# A block is a flat-layout tree if it starts with `outputs/<pbi>/` and its very
# next line is a file entry rather than one of the three standard directories.
FLAT_TREE_RE = re.compile(
    r"^outputs/\d+/\n(?:[│├└─ ]+.*\n)+",
    re.MULTILINE,
)
STANDARD_DIRS = ("deliverables/", "working/", "logs/")


def retree(text: str) -> tuple[str, int]:
    """Replace flat example trees with the canonical three-directory layout."""
    count = 0

    def sub(m: re.Match) -> str:
        nonlocal count
        block = m.group(0)
        if any(d in block for d in STANDARD_DIRS):
            return block          # already migrated
        count += 1
        return CANONICAL_TREE

    return FLAT_TREE_RE.sub(sub, text), count

# Guard: never double-apply a prose substitution.
def already_migrated(text: str, replacement: str) -> bool:
    return replacement in text


def process(path: Path) -> tuple[str, int]:
    original = path.read_text(encoding="utf-8")
    text = original
    count = 0

    for pattern, replacement in CODE_SUBS:
        text, n = re.subn(pattern, replacement, text)
        count += n

    for needle, replacement in PROSE_SUBS:
        if needle in text:
            # Skip if the needle only appears as part of the already-correct form.
            occurrences = text.count(needle) - text.count(replacement)
            if occurrences > 0:
                text = text.replace(needle, replacement)
                count += occurrences

    text, n = retree(text)
    count += n

    return text, count


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    targets = sorted(AGENT_DIR.glob("*.md")) + sorted(SKILL_DIR.glob("*.md"))
    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"Retarget agent output paths — {mode}")
    print("=" * 70)

    total = 0
    for path in targets:
        text, count = process(path)
        rel = path.relative_to(REPO)
        if count == 0:
            print(f"  --   {rel}")
            continue
        print(f"  {count:>3}  {rel}")
        total += count
        if args.apply:
            path.write_text(text, encoding="utf-8")

    print("=" * 70)
    print(f"{total} substitution(s) across {len(targets)} file(s)")
    if not args.apply:
        print("Dry run only. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
