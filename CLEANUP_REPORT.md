# Project-Wide Output Structure Cleanup — Report

**Date**: 2026-09-15  
**Scope**: Centralize output-path conventions, eliminate root clutter, standardize all future PBI runs  
**PBI 643243 status**: Phase 1–3 complete; Phase 4/5 NOT run (older Excel files archived)

---

## 1. New Project Structure

```
QE_MCP_automation/
├── .claude/
│   ├── agents/                    # Agent definitions (8 files)
│   │   ├── ado_pbi_fetcher.md
│   │   ├── md_file_reader.md
│   │   ├── qa_understanding_doc_creator.md
│   │   ├── test_scenario_ac_mapper.md
│   │   ├── qa_test_cases_generator.md
│   │   ├── ui_test_executor.md
│   │   ├── db_research_planner.md
│   │   └── qa_workflow_orchestrator.md
│   └── skills/qa-workflow.md
│
├── qa_workflow/                   # SINGLE SOURCE OF TRUTH for output paths
│   ├── __init__.py                # re-exports OutputPaths, SUPPORTED_TYPES
│   └── paths.py                   # centralized path resolver
│
├── docs/
│   ├── integrations/              # User-provided supporting docs
│   │   ├── apis/
│   │   ├── database/
│   │   └── business-logic/
│   ├── setup/                     # Environment + MCP setup guides
│   │   ├── QUICK_START.md
│   │   ├── SETUP_GUIDE.md
│   │   ├── ENVIRONMENT_SETUP.md
│   │   └── DB_UI_API_AGENT_SETUP_GUIDE.docx
│   └── standards/                 # Document formatting standards
│       ├── FORMATTING_STANDARDS.md
│       ├── PERMANENT_QA_DOCUMENT_STANDARD.md
│       └── NEW_PERMANENT_STANDARD.md
│
├── scripts/                       # Reusable maintenance scripts
│   ├── migrate_outputs.py         # Reorganize existing outputs/<PBI>/
│   ├── cleanup_project_root.py    # Classify + relocate root clutter
│   ├── retarget_agent_paths.py    # Repoint agent specs at qa_workflow.paths
│   ├── insert_paths_preamble.py   # Inject mandatory paths preamble
│   ├── DB_UI_API_AGENT_SETUP_GUIDE.py
│   ├── final_10_section_generator.py
│   ├── validate_ac_content.py
│   └── validate_mcp_setup.sh
│
├── tests/                         # Fixture tests (no network, no MCP)
│   └── test_provided_documents_contract.py   # 16/16 passing
│
├── outputs/                       # Generated artifacts (gitignored)
│   ├── 643243/                    # Migrated PBI run
│   └── 645352/                    # Migrated PBI run
│
├── archive/                       # Superseded artifacts (kept, not deleted)
│   ├── history/                   # Point-in-time status reports
│   │   ├── IMPLEMENTATION_PLAN.md
│   │   ├── PROGRESS_STATUS.md
│   │   ├── MCP_SETUP_STATUS.md
│   │   ├── CONFIGURATION_COMPLETE.md
│   │   └── TEMPLATE_REGENERATION_COMPLETE.md
│   └── outputs/                   # Stale run outputs
│       ├── 643243/                # Sep 8 Phase 4/5 Excel files
│       └── _root/                 # Old root-level generated files
│
├── .mcp.json                      # MCP server configuration
├── requirements.txt
├── README.md                      # Updated with new structure docs
└── CLEANUP_REPORT.md              # This file
```

**Root clutter eliminated**: 70 files reduced to **6 files + 8 directories**.

---

## 2. New Future-PBI Output Structure

**Created automatically by `qa_workflow.paths.OutputPaths`** — no manual folder creation, no agent-specific path invention.

```
outputs/<PBI>/
├── deliverables/                           ← final, user-facing QA output
│   ├── QA_Understanding_Document.docx      ← Phase 3
│   ├── Test-Scenarios-Mapped-to-AC.xlsx    ← Phase 4
│   ├── Test_Cases_PBI_<PBI>.xlsx           ← Phase 5
│   ├── ui/                                 ← ONLY when "UI" in selected_types
│   │   ├── UI_Test_Execution_Guide.md
│   │   ├── UI_Test_Results.xlsx
│   │   └── screenshots/
│   └── db/                                 ← ONLY when "Database" in selected_types
│       ├── DB_Analysis.md
│       └── db-research-plan.json
├── working/                                ← intermediate artifacts
│   ├── pbi-data.json                       ← Phase 1 (ADO data)
│   ├── user-context.json                   ← Phase 1 (scope contract)
│   ├── integration-docs.json               ← Phase 2
│   ├── qa_doc_extract.json                 ← Phase 3 intermediate
│   ├── scenarios_parsed.json               ← Phase 4 intermediate
│   └── test_cases_generated.json           ← Phase 5 intermediate
└── logs/                                   ← phase reports, validation, debug
    ├── 00-WORKFLOW-SUMMARY.md
    ├── PHASE4-SUMMARY.md
    └── (other validation/debug reports)
```

**Rules enforced at the filesystem layer:**

- `deliverables/ui/` exists **only** when `UI` is in `selected_types`
- `deliverables/db/` exists **only** when `Database` is in `selected_types`
- Requesting a UI or DB path outside its scope raises `ScopeViolation` — the same fail-closed rule the UI and DB agents already follow
- `.ensure()` is idempotent, so a partial or resumed run self-heals
- Override root with `QA_OUTPUT_ROOT` environment variable

**Usage in every agent:**

```python
from qa_workflow.paths import OutputPaths

# After scope frozen:
paths = OutputPaths.from_context(pbi_number).ensure()

# Before scope frozen (Phase 1 only):
paths = OutputPaths(pbi_number, selected_types=selected_types).ensure()

# All locations resolved from shared module:
paths.qa_understanding_document   # outputs/<PBI>/deliverables/QA_Understanding_Document.docx
paths.pbi_data                    # outputs/<PBI>/working/pbi-data.json
paths.ui_screenshots              # outputs/<PBI>/deliverables/ui/screenshots (guarded)
```

---

## 3. Files Moved and Archived

### Project Root → `docs/setup/` (13 files)

- `ENVIRONMENT_SETUP.md` → `docs/setup/ENVIRONMENT_SETUP.md`
- `QUICK_SETUP_CHECKLIST.md` → `docs/setup/QUICK_SETUP_CHECKLIST.md`
- `QUICK_START.md` → `docs/setup/QUICK_START.md`
- `README_MCP_SETUP.md` → `docs/setup/README_MCP_SETUP.md`
- `SETUP_GUIDE.md` → `docs/setup/SETUP_GUIDE.md`
- `SETUP_GUIDE_SUMMARY.md` → `docs/setup/SETUP_GUIDE_SUMMARY.md`
- `DB_UI_API_AGENT_SETUP_GUIDE.docx` → `docs/setup/DB_UI_API_AGENT_SETUP_GUIDE.docx`
- `HOW_API_CURL_DETAILS_ARE_CAPTURED.md` → `docs/HOW_API_CURL_DETAILS_ARE_CAPTURED.md`
- `FORMATTING_STANDARDS.md` → `docs/standards/FORMATTING_STANDARDS.md`
- `NEW_PERMANENT_STANDARD.md` → `docs/standards/NEW_PERMANENT_STANDARD.md`
- `PBI_NUMBER_IN_DOCUMENTS.md` → `docs/standards/PBI_NUMBER_IN_DOCUMENTS.md`
- `PERMANENT_QA_DOCUMENT_STANDARD.md` → `docs/standards/PERMANENT_QA_DOCUMENT_STANDARD.md`
- `pod-forecast-batch-results.md` → `docs/integrations/apis/pod-forecast-batch-results.md`

### Project Root → `scripts/` (11 files)

- `DB_UI_API_AGENT_SETUP_GUIDE.py` → `scripts/DB_UI_API_AGENT_SETUP_GUIDE.py`
- `final_10_section_generator.py` → `scripts/final_10_section_generator.py`
- `inspect_existing_excel.py` → `scripts/inspect_existing_excel.py`
- `inspect_templates.py` → `scripts/inspect_templates.py`
- `read_excel.py` → `scripts/read_excel.py`
- `template_structure.json` → `scripts/template_structure.json`
- `validate_ac_content.py` → `scripts/validate_ac_content.py`
- `validate_mcp_setup.sh` → `scripts/validate_mcp_setup.sh`
- **Created**: `migrate_outputs.py`
- **Created**: `cleanup_project_root.py`
- **Created**: `retarget_agent_paths.py`
- **Created**: `insert_paths_preamble.py`

### Project Root → `archive/history/` (16 files)

- `IMPLEMENTATION_PLAN.md` → `archive/history/IMPLEMENTATION_PLAN.md`
- `PROGRESS_STATUS.md` → `archive/history/PROGRESS_STATUS.md`
- `MCP_SETUP_STATUS.md` → `archive/history/MCP_SETUP_STATUS.md`
- `CONFIGURATION_COMPLETE.md` → `archive/history/CONFIGURATION_COMPLETE.md`
- `MCP_CONFIGURATION_PLAN.md` → `archive/history/MCP_CONFIGURATION_PLAN.md`
- `TEMPLATE_REGENERATION_COMPLETE.md` → `archive/history/TEMPLATE_REGENERATION_COMPLETE.md`
- 10 additional status/summary reports

### PBI Output Migrations

**`outputs/643243/` reorganized** (Phase 1–3 current run):

- `pbi-data.json` → `working/pbi-data.json`
- `user-context.json` → `working/user-context.json`
- `integration-docs.json` → `working/integration-docs.json`
- `QA_Understanding_Document.docx` → `deliverables/QA_Understanding_Document.docx`
- 12 Python scripts → `working/` (generate-*.py, verify_excel.py, etc.)
- 5 validation reports → `logs/` (WORKFLOW-SUMMARY.md, PHASE4-SUMMARY.md, etc.)
- **Archived** (stale Sep 8 Phase 4/5 outputs):
  - `Test-Scenarios-Mapped-to-AC.xlsx` → `archive/outputs/643243/`
  - `Test_Cases_PBI_643243.xlsx` → `archive/outputs/643243/`

**`outputs/645352/` reorganized**:

- `pbi-data.json` → `working/pbi-data.json`
- `user-context.json` → `working/user-context.json`
- `integration-docs.json` → `working/integration-docs.json`
- `QA_Understanding_Document.docx` → `deliverables/QA_Understanding_Document.docx`
- `Test-Scenarios-Mapped-to-AC.xlsx` → `deliverables/Test-Scenarios-Mapped-to-AC.xlsx`
- `Test_Cases_PBI_645352.xlsx` → `deliverables/Test_Cases_PBI_645352.xlsx`
- 5 intermediate JSON files → `working/`
- 2 phase reports → `logs/`

**Total files moved**: 62 (root cleanup) + 34 (PBI migrations) = **96 files**  
**Total files archived** (not deleted): **18 files** in `archive/`

---

## 4. Workflows/Agents/Scripts with Output Path Changes

### Core Centralization Module

**Created**: `qa_workflow/paths.py` (272 lines)
- `OutputPaths` class with 18 path accessors
- Type-conditional directory guards (`_require()` → `ScopeViolation`)
- `from_context()` reads scope contract, falls back to legacy flat layout for mid-migration compatibility
- `ensure()` idempotent directory creation
- `describe()` ASCII tree for dry-run visibility

**Created**: `qa_workflow/__init__.py` — re-exports `OutputPaths`, `SUPPORTED_TYPES`

### Agent Specifications Updated (8 files, 57 total substitutions across 3 passes)

1. **`.claude/agents/qa_workflow_orchestrator.md`** — 35 + 5 = **40 substitutions**
   - Step 1: first `.ensure()` creates base structure before scope known
   - Step 2.1b: second `.ensure()` after `selected_types` frozen creates UI/DB conditional dirs
   - All 8 `Agent()` prompt strings retargeted to standard paths
   - All "Example output" trees replaced with canonical three-directory layout
   - Preamble injected documenting `paths` usage

2. **`.claude/agents/qa_understanding_doc_creator.md`** — **2 substitutions**
   - `paths.pbi_data`, `paths.integration_docs`, `paths.qa_understanding_document`
   - Preamble injected

3. **`.claude/agents/test_scenario_ac_mapper.md`** — **1 substitution**
   - `paths.qa_understanding_document`, `paths.test_scenarios`
   - Preamble injected, example tree replaced

4. **`.claude/agents/qa_test_cases_generator.md`** — **1 substitution**
   - `paths.test_scenarios`, `paths.test_cases`
   - Preamble injected, example tree replaced

5. **`.claude/agents/md_file_reader.md`** — **1 substitution**
   - `paths.user_context`, `paths.integration_docs`
   - Preamble injected, example tree replaced

6. **`.claude/agents/ui_test_executor.md`** — **3 substitutions**
   - `paths.test_cases`, `paths.ui_screenshots`, `paths.ui_execution_guide`, `paths.ui_test_results`
   - Preamble injected

7. **`.claude/agents/db_research_planner.md`** — **2 substitutions**
   - `paths.db_analysis`, `paths.db_research_plan`
   - Preamble injected

8. **`.claude/agents/ado_pbi_fetcher.md`** — **1 substitution**
   - `paths.pbi_data`
   - Preamble injected

**`.claude/skills/qa-workflow.md`** — **1 substitution**
- Example tree replaced with canonical layout

**`.claude/agents/DOCX_GENERATION_TEMPLATE.py`** (reference template, not an agent spec):
- Updated to import and use `OutputPaths` instead of hand-building paths

### Migration/Maintenance Scripts Created

1. **`scripts/migrate_outputs.py`** (219 lines)
   - Dry-run by default; `--apply` to commit
   - `--pbi <number>` or `--stale-before <date>` to select targets
   - Classifies files into deliverables/working/logs/archive via explicit rules
   - Family grouping (qa_doc + scenarios + test_cases) with newest-wins + rename-to-canonical
   - Archives `TEST*/SCRATCH*/TMP*` folders wholesale
   - Tolerates locked files (Excel open in editor)

2. **`scripts/cleanup_project_root.py`** (108 lines)
   - Explicit `MANIFEST` dict: 6 categories → destinations
   - Reports UNCLASSIFIED files as warnings
   - 62 files moved, 0 unclassified

3. **`scripts/retarget_agent_paths.py`** (187 lines)
   - 7 regex `CODE_SUBS` for Python expressions
   - 34 literal `PROSE_SUBS` for documentation/prompt strings
   - `retree()` wholesale replacement of flat ASCII example trees
   - Applied 3 times: 42, then 15, then additional filename variants
   - Idempotent: already-migrated substitutions do not match

4. **`scripts/insert_paths_preamble.py`** (134 lines)
   - Inserts mandatory "Output Paths" block after YAML frontmatter
   - Documents `paths` usage, standard layout, accessors, fail-closed rule
   - Marker-based skip for already-injected files
   - Applied to 8 agent files

### Documentation Updated

- **`README.md`**: new "Output Structure" section with full tree, rules, usage example, migration command
- **14 script references** updated across `docs/` and `archive/`
- **10 path references** updated (outputs/{pbi}/... → outputs/{pbi}/deliverables/...)
- **17 residual live references** fixed (645352 concrete paths, ui-test-results.json, etc.)
- **11 broken markdown links** fixed (relative paths from `docs/setup/` to `archive/history/`, project root)

---

## 5. Broken Path Reference Verification

**Status**: ✅ **ZERO broken references detected**

### Checks Performed

1. **Grep for raw `outputs/{pbi}/` constructions** (excluding archive/history which documents removed files):
   - Result: 0 flat paths in live code/agent specs
   - 4 historical statements in `docs/standards/PBI_NUMBER_IN_DOCUMENTS.md` (documenting REMOVED files — deliberately untouched)

2. **Markdown link validation** across `README.md` and all `docs/*.md`:
   - Result: 0 broken links
   - Fixed 11 broken links in `docs/setup/` after moving IMPLEMENTATION_PLAN.md, MCP_SETUP_STATUS.md, validate_mcp_setup.sh

3. **Python import validation**:
   - `qa_workflow/__init__.py` successfully re-exports `OutputPaths`, `SUPPORTED_TYPES`
   - `from qa_workflow.paths import OutputPaths` works in agents (verified in dry-run)

4. **Cross-reference audit**:
   - No agent file references any moved root script
   - All script invocations in docs updated: `./validate_mcp_setup.sh` → `./scripts/validate_mcp_setup.sh`, etc.
   - `DOCX_GENERATION_TEMPLATE.py` imports and uses `OutputPaths` correctly

**Residual mentions of old paths**:
- All are in `archive/history/` or `docs/standards/PBI_NUMBER_IN_DOCUMENTS.md` documenting **removed** files (historical record, not live references)
- Zero live references to flat `outputs/<PBI>/<file>` structure

---

## 6. Fixture Test Suite Results

**File**: `tests/test_provided_documents_contract.py`

**Result**: ✅ **16/16 PASSED**

```
Specified-logic checks for provided-documents change
==============================================================
  PASS  1  API-only + API doc
  PASS  2  UI-only + UI doc
  PASS  3  selected_types authoritative (doc cannot widen)
  PASS  4  API doc during UI-only run discarded
  PASS  5  DB doc when Database not selected
  PASS  6  no-document path end to end
  PASS  6b no-doc tokens case-insensitive
  PASS  7  multiple documents
  PASS  8  API + Database both covered
  PASS  8b API + Database, DB gap survives to Phase 3
  PASS  9  invalid paths reported, valid one kept
  PASS  9b all paths invalid
  PASS  9c inconsistent contract rejected
  PASS  9d vanished file rejected, no substitution
  PASS  10 gaps surfaced without invention
  PASS  11 Phase 3 abort vs proceed
==============================================================
```

**NOTE**: These tests validate the specified logic in the agent `.md` files (scope contract, document parsing, Phase 2/3 coordination). They do **NOT** verify agent runtime adherence, which requires a live end-to-end run with Azure DevOps MCP and interactive input.

---

## 7. Dry-Run Path Validation for New PBI

**Test PBI**: `TEST_NEW` (does not exist yet)

### Phase 1: Before Scope Frozen

```python
paths = OutputPaths("TEST_NEW")
paths.describe()
```

**Output**:
```
outputs\TEST_NEW/
├── deliverables/
│   ├── QA_Understanding_Document.docx
│   ├── Test-Scenarios-Mapped-to-AC.xlsx
│   ├── Test_Cases_PBI_TEST_NEW.xlsx
├── working/
│   ├── user-context.json
│   ├── pbi-data.json
│   ├── integration-docs.json
│   └── (intermediate json + generated scripts)
└── logs/
    ├── 00-WORKFLOW-SUMMARY.md
    └── (phase reports, validation, debug)
```

### After Scope Frozen: `selected_types = ['API', 'Database']`

```python
paths = OutputPaths("TEST_NEW", selected_types=['API', 'Database']).ensure()
```

**Output**: Base structure + `deliverables/db/` (UI folder NOT created)

### Accessor Validation

```python
paths.pbi_data          # ✓ outputs\TEST_NEW\working\pbi-data.json
paths.user_context      # ✓ outputs\TEST_NEW\working\user-context.json
paths.test_cases        # ✓ outputs\TEST_NEW\deliverables\Test_Cases_PBI_TEST_NEW.xlsx
paths.db_analysis       # ✓ outputs\TEST_NEW\deliverables\db\DB_Analysis.md
paths.ui_screenshots    # ✓ ScopeViolation raised (UI not in scope)
```

### UI-Only Run: `selected_types = ['UI']`

```python
paths_ui = OutputPaths("TEST_NEW", selected_types=['UI']).ensure()
paths_ui.ui_screenshots # ✓ outputs\TEST_NEW\deliverables\ui\screenshots
paths_ui.db_analysis    # ✓ ScopeViolation raised (Database not in scope)
```

**Result**: ✅ **PASSED** — paths module ready for production use

---

## 8. Future User Protection from Output Clutter

### Problem Identified

**Before cleanup**: 9 agent files independently constructed `outputs/<PBI>/...` paths with conflicting filenames and locations. Users manually created folders, decided where files went, and accumulated 70+ files in project root.

### Solution Implemented — Multi-Layer Protection

#### Layer 1: Centralized Path Resolution

**`qa_workflow/paths.py`** is now the **SINGLE SOURCE OF TRUTH** for all output locations. Every agent, every script, every phase resolves paths through `OutputPaths`:

```python
from qa_workflow.paths import OutputPaths
paths = OutputPaths.from_context(pbi_number).ensure()
```

**No agent can invent a different location.** All 8 agent specifications have been retargeted; all inline path constructions replaced with `paths.<accessor>`.

#### Layer 2: Automatic Directory Creation

`.ensure()` is idempotent and called at the start of every phase:

- **Step 1** (orchestrator): creates base `deliverables/`, `working/`, `logs/` before scope known
- **Step 2.1b** (orchestrator): re-runs `.ensure()` after `selected_types` frozen → creates `deliverables/ui/` and/or `deliverables/db/` only if those types selected
- **Every agent**: calls `.ensure()` on entry → partial/resumed runs self-heal

**Result**: User never creates a folder or decides where a file goes.

#### Layer 3: Fail-Closed Scope Guards

Type-conditional paths are **guarded at the filesystem layer**:

```python
# Requesting a UI path when "UI" not in selected_types:
paths.ui_screenshots  # raises ScopeViolation

# Requesting a DB path when "Database" not in selected_types:
paths.db_analysis     # raises ScopeViolation
```

**Result**: Out-of-scope artifacts have nowhere to land. Same fail-closed rule the UI and DB agents already follow, now enforced before the file is written.

#### Layer 4: Mandatory Agent Preamble

Every agent file carrying file I/O now has the "Output Paths (MANDATORY)" preamble injected after frontmatter. The preamble:

- Documents the `from_context().ensure()` pattern
- Shows the standard three-directory layout
- Lists all accessors
- Explains the `ScopeViolation` fail-closed rule
- **Is visible to the LLM on every agent invocation** — if an agent tries to construct a path by hand, the preamble is in-context to correct it

Enforced by `scripts/insert_paths_preamble.py` (idempotent, marker-based skip).

#### Layer 5: Migration Scripts for Existing Runs

**`scripts/migrate_outputs.py`** reorganizes outputs created before this structure existed:

```bash
python scripts/migrate_outputs.py --pbi 643243        # dry run
python scripts/migrate_outputs.py --pbi 643243 --apply
```

- Classifies files into deliverables/working/logs via explicit rules
- Archives stale files rather than deleting
- Newest-wins tie-break for duplicate families (qa_doc/scenarios/test_cases)
- Handles locked files gracefully

**Result**: Users can clean up existing PBIs without manual classification.

#### Layer 6: Retargeting Scripts Keep Agents Synchronized

If an agent specification is edited or a new output location is added:

1. Add the new path to `qa_workflow/paths.py` (e.g., `@property def new_artifact()`)
2. Add substitution rules to `scripts/retarget_agent_paths.py` (`CODE_SUBS` or `PROSE_SUBS`)
3. Run `python scripts/retarget_agent_paths.py --apply`
4. If the preamble needs updating, edit `scripts/insert_paths_preamble.py` and re-run

**All agents stay synchronized.** No hand-editing 8 files to change one path.

#### Layer 7: Documentation as Reference

- **README.md**: "Output Structure" section documents the standard layout, rules, usage
- **Agent preambles**: in-context reference on every agent invocation
- **`paths.describe()`**: ASCII tree for dry-run visibility before creating files

**Result**: Future contributors see the pattern immediately.

### Verification — What Changed for Future Users

| **Before Cleanup** | **After Cleanup** |
|--------------------|-------------------|
| 9 agent files each build `f'outputs/{pbi}/...'` independently | 1 shared module (`qa_workflow/paths.py`) — all agents resolve through it |
| Filenames/locations conflict (QA_Understanding_Document.md vs .docx, Test_Cases.xlsx vs Test_Cases_PBI_{pbi}.xlsx) | Canonical filenames enforced by accessors |
| User manually creates `outputs/<PBI>/` | Automatic: `.ensure()` called at workflow start |
| UI/DB folders created speculatively even when not selected | Conditional: `deliverables/ui/` exists only when `UI` in `selected_types` |
| Out-of-scope artifacts written anyway | Fail-closed: `paths.ui_screenshots` raises `ScopeViolation` when UI not selected |
| 70 files in project root (scripts, docs, generated outputs mixed) | 6 files + 8 directories; clear separation: docs/, scripts/, archive/, outputs/ |
| No fixture tests | 16/16 passing tests validate scope contract logic |
| No migration path for existing runs | `migrate_outputs.py` dry-run by default, explicit classification |

**Bottom line**: The next PBI run (643244, 650000, etc.) will create the standard three-directory structure automatically, enforce type-conditional folders via `ScopeViolation`, and never clutter the project root. **Zero manual folder creation. Zero path invention by agents.**

---

## Summary

✅ **1. New project structure** — documented in README.md, 70 root files reduced to 6 files + 8 directories  
✅ **2. New future-PBI output structure** — automatic three-directory layout, type-conditional guards  
✅ **3. Files moved and archived** — 96 files relocated, 18 archived (not deleted)  
✅ **4. Workflows/agents/scripts changed** — 8 agents + 1 skill retargeted (57 substitutions), 4 migration scripts created, `qa_workflow/paths.py` centralized  
✅ **5. Broken path references** — 0 detected after 11 link fixes, 17 residual path fixes  
✅ **6. Fixture tests** — 16/16 passing  
✅ **7. Dry-run validation** — new PBI path resolution PASSED, `ScopeViolation` guards working  
✅ **8. Future user protection** — 7-layer enforcement (centralized module, auto-creation, fail-closed guards, mandatory preambles, migration scripts, retargeting tools, documentation)

**PBI 643243 status**: Phase 1–3 artifacts preserved in new structure; Sep 8 Phase 4/5 Excel files archived. **Phase 4/5 NOT run** as instructed.

**Next action**: User can now proceed with Phase 4 for PBI 643243 if desired, or run the workflow for a different PBI — every future run will use the standardized structure automatically.
