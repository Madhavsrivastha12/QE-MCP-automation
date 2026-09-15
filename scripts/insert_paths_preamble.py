"""
Insert the mandatory "Output Paths" preamble into every agent specification that
resolves output locations.

The preamble defines `paths`, which the retargeted code blocks reference. Run
this after scripts/retarget_agent_paths.py.

    python scripts/insert_paths_preamble.py
    python scripts/insert_paths_preamble.py --apply

Idempotent: files already carrying the marker are skipped.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
AGENT_DIR = REPO / ".claude" / "agents"

MARKER = "## Output Paths (MANDATORY"

PREAMBLE = '''
---

## Output Paths (MANDATORY — read this before any file I/O)

**Never build an `outputs/...` path by hand.** Every location comes from one
shared module, so all agents agree on where things go and every run gets the
standard structure automatically. The user never creates a folder.

```python
from qa_workflow.paths import OutputPaths

pbi_number = "<pbi>"                       # supplied by the orchestrator
paths = OutputPaths.from_context(pbi_number).ensure()
```

`from_context()` reads `selected_types` out of the scope contract, so the
type-conditional directories exist only when that type is selected.
`.ensure()` is idempotent — call it at the start of every phase and a partial or
resumed run self-heals.

Phase 1 agents that run *before* the contract exists build it directly instead:

```python
paths = OutputPaths(pbi_number, selected_types=selected_types).ensure()
```

Standard layout for every PBI:

```
outputs/<PBI>/
├── deliverables/     final, user-facing QA output
│   ├── ui/           ONLY when "UI" in selected_types
│   └── db/           ONLY when "Database" in selected_types
├── working/          intermediate artifacts (contracts, parsed json, generators)
└── logs/             phase reports, validation, debug history
```

Accessors: `paths.user_context`, `paths.pbi_data`, `paths.integration_docs`,
`paths.qa_understanding_document`, `paths.test_scenarios`, `paths.test_cases`,
`paths.ui_screenshots`, `paths.ui_execution_guide`, `paths.ui_test_results`,
`paths.db_research_plan`, `paths.db_analysis`, `paths.workflow_summary`,
plus `paths.working_file(name)`, `paths.deliverable_file(name)`,
`paths.log_file(name)`.

Requesting a UI or DB path when that type is **not** in `selected_types` raises
`ScopeViolation`. That is deliberate: it is the same fail-closed rule the UI and
DB agents already follow, enforced at the filesystem layer so out-of-scope
artifacts have nowhere to land.
'''

TARGETS = [
    "ado_pbi_fetcher.md",
    "db_research_planner.md",
    "md_file_reader.md",
    "qa_test_cases_generator.md",
    "qa_understanding_doc_creator.md",
    "qa_workflow_orchestrator.md",
    "test_scenario_ac_mapper.md",
    "ui_test_executor.md",
]


def insert(text: str) -> str:
    """Place the preamble immediately after the YAML frontmatter block."""
    if not text.startswith("---"):
        return PREAMBLE.lstrip("\n") + "\n" + text

    end = text.find("\n---", 3)
    if end == -1:
        return PREAMBLE.lstrip("\n") + "\n" + text
    cut = text.find("\n", end + 1) + 1
    return text[:cut] + PREAMBLE + text[cut:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    print(f"Insert Output Paths preamble — {'APPLY' if args.apply else 'DRY RUN'}")
    print("=" * 70)

    changed = 0
    for name in TARGETS:
        path = AGENT_DIR / name
        if not path.exists():
            print(f"  ----  {name} (not found)")
            continue
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            print(f"  SKIP  {name} (already present)")
            continue
        print(f"  ADD   {name}")
        changed += 1
        if args.apply:
            path.write_text(insert(text), encoding="utf-8")

    print("=" * 70)
    print(f"{changed} file(s) updated")
    if not args.apply:
        print("Dry run only. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
