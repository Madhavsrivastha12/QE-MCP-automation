"""
One-time reorganisation of the project root into a maintainable structure.

Every file is classified explicitly in the MANIFEST below — nothing is matched
by a wildcard and nothing is deleted. Files move to:

    scripts/            active, reusable tooling
    docs/setup/         installation and environment guides
    docs/standards/     document/format standards still in force
    docs/               current reference material
    archive/history/    point-in-time reports, plans, completion summaries
    archive/legacy-scripts/  one-off generators superseded by the agents

Dry-run by default; pass --apply to move.

    python scripts/cleanup_project_root.py
    python scripts/cleanup_project_root.py --apply

Re-running is safe: files already at their destination are reported and skipped.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------- manifest
# category -> (destination, [filenames])
MANIFEST: dict[str, tuple[str, list[str]]] = {
    "active project/configuration": ("", [
        # Stay at the repository root. Listed for completeness; never moved.
        ".gitignore", ".mcp.json", "package.json", "package-lock.json",
        "requirements.txt", "README.md",
    ]),

    "active reusable scripts": ("scripts", [
        "validate_mcp_setup.sh",
        "DB_UI_API_AGENT_SETUP_GUIDE.py",   # regenerates the setup guide .docx
        "final_10_section_generator.py",    # referenced by docs/standards/
        "read_excel.py",
        "inspect_existing_excel.py",
        "inspect_templates.py",
        "validate_ac_content.py",
        "template_structure.json",          # consumed by the generator above
    ]),

    "documentation — setup": ("docs/setup", [
        "ENVIRONMENT_SETUP.md",
        "QUICK_START.md",
        "SETUP_GUIDE.md",
        "README_MCP_SETUP.md",
        "QUICK_SETUP_CHECKLIST.md",
        "SETUP_GUIDE_SUMMARY.md",
        "DB_UI_API_AGENT_SETUP_GUIDE.docx",
    ]),

    "documentation — standards": ("docs/standards", [
        "FORMATTING_STANDARDS.md",
        "PERMANENT_QA_DOCUMENT_STANDARD.md",
        "NEW_PERMANENT_STANDARD.md",
        "PBI_NUMBER_IN_DOCUMENTS.md",
    ]),

    "documentation — reference": ("docs", [
        "HOW_API_CURL_DETAILS_ARE_CAPTURED.md",
    ]),

    "historical/legacy reports": ("archive/history", [
        "COMPLETION_SUMMARY.md",
        "CONFIGURATION_COMPLETE.md",
        "EXCEL_FORMAT_MIGRATION_COMPLETE.md",
        "FINAL_REGRESSION_TEST_RESULTS.md",
        "REGRESSION_TEST_RESULTS.md",
        "IMPLEMENTATION_PLAN.md",
        "PROGRESS_STATUS.md",
        "PHASE_1_UPDATE_COMPLETE.md",
        "QA_WORKFLOW_ALIAS_CREATED.md",
        "REDESIGN_IMPLEMENTATION_COMPLETE.md",
        "TEMPLATE_ANALYSIS_AND_PLAN.md",
        "TEMPLATE_REGENERATION_COMPLETE.md",
        "TEST_IMPLEMENTATION.md",
        "UI_DB_AGENT_INTEGRATION_ANALYSIS.md",
        "UI_DB_INTEGRATION_COMPLETE.md",
        "WORKFLOW_REVIEW_ANALYSIS.md",
        "WORKFLOW_TEMPLATE_UPDATE_COMPLETE.md",
        "WORKFLOW_TESTING_TYPES_REVIEW.md",
        "MCP_SETUP_STATUS.md",
        "README_UPDATED.md",             # superseded duplicate of README.md
    ]),

    "legacy scripts superseded by agents": ("archive/legacy-scripts", [
        "clean_reference_generator.py",
        "convert_md_to_docx.py",
        "convert_qa_to_word.py",
        "create_test_scenario_excel.py",
        "exact_template_generator.py",
        "extract_scenarios.py",
        "fetch_pbi.py",
        "fetch_pbi_enhanced.js",
        "final_10_section_generator.py.backup",
        "final_10_section_generator.py.old",
        "final_10_section_generator.py.previous",
        "generate_enhanced_qa_document.py",
        "generate_qa_word_document.py",
        "generate_test_cases_test3.py",
        "generate_test_scenarios.js",
        "generate_test_scenarios.py",
        "generate_test_scenarios_645352.py",
        "reference_template_generator.py",
        "template_based_generator.py",
        "migrate_excel_format.py",       # one-off; migration already completed
        "validate_migration.py",         # validated that one-off migration
        "run_excel_gen.sh",
    ]),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="Actually move files")
    args = ap.parse_args()

    mode = "APPLY" if args.apply else "DRY RUN (nothing will be moved)"
    print(f"Project root cleanup — {mode}")
    print("=" * 70)

    moved = skipped = missing = 0
    claimed: set[str] = set()

    for category, (dest_rel, names) in MANIFEST.items():
        print(f"\n{category}  ->  {dest_rel or '(stays at root)'}")
        for name in names:
            claimed.add(name)
            src = REPO / name
            if not dest_rel:
                print(f"  KEEP   {name}")
                continue
            if not src.exists():
                print(f"  ----   {name} (not present)")
                missing += 1
                continue
            dst = REPO / dest_rel / name
            if dst.exists():
                print(f"  SKIP   {name} (already at {dest_rel}/)")
                skipped += 1
                continue
            print(f"  MOVE   {name}  ->  {dest_rel}/")
            if args.apply:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
            moved += 1

    # Anything at the root the manifest does not mention.
    unclaimed = sorted(
        p.name for p in REPO.iterdir()
        if p.is_file() and p.name not in claimed
    )
    if unclaimed:
        print("\nUNCLASSIFIED — left at root, review manually:")
        for name in unclaimed:
            print(f"  ?      {name}")

    print("\n" + "=" * 70)
    print(f"{moved} moved, {skipped} already in place, {missing} absent, "
          f"{len(unclaimed)} unclassified")
    if not args.apply:
        print("Dry run only. Re-run with --apply to perform these moves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
