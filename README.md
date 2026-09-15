# QE MCP Automation - QA Testing Agent Flow

Multi-agent QA testing workflow with Azure DevOps integration for automated test case generation from PBI requirements.

---

## ⚡ TL;DR - How to Run

```bash
@qa-workflow <PBI_NUMBER>
```

**Example**:
```bash
@qa-workflow 643243
```

That's it! The workflow handles everything automatically with 2 user review checkpoints.

**Output**: `outputs/643243/deliverables/` containing:
- Professional Word QA document (10 sections)
- Test scenario mapping (Excel)
- Azure DevOps test cases (Excel)

Every run creates the same three-folder structure automatically — you never make
a folder or decide where a file goes. See [Output Structure](#-output-structure).

---

## 🎯 Overview

This project automates the QA testing workflow by:
1. Fetching PBI (Product Backlog Item) from Azure DevOps
2. Reading integration documentation (API, Database, Business Logic)
3. Creating comprehensive QA understanding documents
4. Mapping test scenarios to Acceptance Criteria
5. Generating detailed test cases in Excel format

## 📋 Quick Start

### Prerequisites

1. **Azure DevOps PAT Token**
   
   Set as Windows environment variable (NOT in .env file):
   ```powershell
   # PowerShell (run as current user)
   [System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-token-here', 'User')
   ```
   
   Then restart Claude Code to pick up the environment variable.

2. **MCP Servers** (Already configured in `.mcp.json`)
   - Azure DevOps MCP (`@azure-devops/mcp`)
   - Usage Empire MCP (from parent repo at `C:\UE_Automation\usage-empire`)

### How to Run

**Simple Command** (Recommended):
```bash
@qa-workflow <PBI_NUMBER>
```

**Example**:
```bash
@qa-workflow 643243
```

**Alternative** (Same result, longer command):
```bash
@qa-workflow-orchestrator 643243
```

**What Happens**:
1. Fetches PBI from Azure DevOps → `pbi-data.json`
2. Reads integration documentation → `integration-docs.json`
3. Creates QA Understanding Document → `QA_Understanding_Document.docx` (Professional Word format)
4. **[CHECKPOINT 1]** - User reviews QA doc (Approve/Request Changes/Cancel)
5. Maps test scenarios to AC → `Test-Scenarios-Mapped-to-AC.xlsx`
6. **[CHECKPOINT 2]** - User reviews scenarios (Approve/Add More/Cancel)
7. Generates test cases → `Test_Cases_PBI_<PBI>.xlsx` (Azure DevOps import-ready)
8. Creates workflow summary → `logs/00-WORKFLOW-SUMMARY.md`

## 📁 Project Structure

```
QE_MCP_automation/
├── .claude/
│   ├── agents/                    # Agent definitions
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
├── qa_workflow/                   # Shared Python package
│   └── paths.py                   # SINGLE SOURCE OF TRUTH for output paths
│
├── docs/
│   ├── integrations/              # Integration documentation
│   │   ├── apis/                  # API endpoint docs
│   │   ├── database/              # Database schema docs
│   │   └── business-logic/        # Business logic docs
│   ├── setup/                     # Environment + MCP setup guides
│   └── standards/                 # Document formatting standards
│
├── scripts/                       # Reusable maintenance scripts
│   ├── migrate_outputs.py         # Reorganize an existing outputs/<PBI>/
│   ├── cleanup_project_root.py    # Classify + relocate root clutter
│   ├── retarget_agent_paths.py    # Repoint agent specs at qa_workflow.paths
│   └── insert_paths_preamble.py   # Inject the mandatory paths preamble
│
├── tests/                         # Fixture tests (no network, no MCP)
├── outputs/                       # Generated artifacts (gitignored)
├── archive/                       # Superseded artifacts, kept not deleted
│   ├── history/                   # Point-in-time status reports
│   └── outputs/                   # Stale run outputs
│
├── .mcp.json                      # MCP server configuration
├── requirements.txt
└── README.md                      # This file
```

## 📦 Output Structure

Every PBI run produces exactly this layout. It is created automatically by
`qa_workflow.paths.OutputPaths` — no manual folder creation, and no agent
invents its own location.

```
outputs/<PBI>/
├── deliverables/                           ← final, user-facing QA output
│   ├── QA_Understanding_Document.docx      ← Phase 3
│   ├── Test-Scenarios-Mapped-to-AC.xlsx    ← Phase 4
│   ├── Test_Cases_PBI_<PBI>.xlsx           ← Phase 5
│   ├── ui/                                 ← ONLY when "UI" is selected
│   │   ├── UI_Test_Execution_Guide.md
│   │   ├── UI_Test_Results.xlsx
│   │   └── screenshots/
│   └── db/                                 ← ONLY when "Database" is selected
│       ├── DB_Analysis.md
│       └── db-research-plan.json
├── working/                                ← intermediate artifacts
│   ├── pbi-data.json                       ← Phase 1 (ADO data)
│   ├── user-context.json                   ← Phase 1 (scope contract)
│   └── integration-docs.json               ← Phase 2
└── logs/                                   ← phase reports, validation, debug
    └── 00-WORKFLOW-SUMMARY.md
```

**Rules enforced in code, not by convention:**

- `deliverables/ui/` exists only when `UI` is in `selected_types`;
  `deliverables/db/` only when `Database` is. Asking for a UI or DB path
  outside its scope raises `ScopeViolation` — the same fail-closed rule the UI
  and DB agents follow, enforced at the filesystem layer so an out-of-scope
  artifact has nowhere to land.
- `.ensure()` is idempotent, so a partial or resumed run self-heals.
- Override the root with the `QA_OUTPUT_ROOT` environment variable.

Agents resolve every location through the shared module:

```python
from qa_workflow.paths import OutputPaths
paths = OutputPaths.from_context(pbi_number).ensure()
paths.qa_understanding_document   # outputs/<PBI>/deliverables/QA_Understanding_Document.docx
paths.pbi_data                    # outputs/<PBI>/working/pbi-data.json
paths.workflow_summary            # outputs/<PBI>/logs/00-WORKFLOW-SUMMARY.md
```

To reorganize a run created before this structure existed:

```bash
python scripts/migrate_outputs.py --pbi 643243        # dry run
python scripts/migrate_outputs.py --pbi 643243 --apply
```

## 🤖 Agents

### 1. ADO PBI Fetcher
Fetches PBI from Azure DevOps using MCP tools.

**Input**: PBI number (e.g., 643243)
**Output**: `outputs/<PBI>/working/pbi-data.json`

### 2. MD File Reader
Reads and parses integration documentation.

**Input**: Path to MD files or directory
**Output**: `outputs/<PBI>/working/integration-docs.json`

### 3. QA Understanding Doc Creator
Combines PBI + integration docs into comprehensive QA understanding document.

**Input**: pbi-data.json + integration-docs.json
**Output**: `outputs/<PBI>/deliverables/QA_Understanding_Document.docx` (Professional Word format)

**Features**:
- 10 comprehensive sections
- Professional Word template with navy blue formatting
- Complete AC text (no truncation with "...")
- Dynamic, implementation-focused QA interpretations
- Concrete examples with real dates/timestamps
- Smart page break control
- Dynamic page numbers ("Page X of Y")

### 4. Test Scenario AC Mapper
Maps test scenarios to Acceptance Criteria.

**Input**: QA_Understanding_Document.md
**Output**: `outputs/<PBI>/deliverables/Test-Scenarios-Mapped-to-AC.xlsx`

### 5. Test Cases Generator
Generates detailed test cases.

**Input**: QA_Understanding_Document.md + Test-Scenarios-Mapped-to-AC.xlsx
**Output**: `outputs/<PBI>/deliverables/Test_Cases_PBI_<PBI>.xlsx`

### 6. QA Workflow Orchestrator
Coordinates all 5 agents in sequence with 2 user checkpoints.

**How to Run**:
```bash
@qa-workflow <PBI_NUMBER>
```

**Input**: PBI number (e.g., 643243)

**Output**: Complete deliverables in `outputs/<PBI>/`
- `working/pbi-data.json` - PBI data from Azure DevOps
- `working/integration-docs.json` - Parsed integration documentation
- `deliverables/QA_Understanding_Document.docx` - Professional Word document (10 sections)
- `deliverables/Test-Scenarios-Mapped-to-AC.xlsx` - Scenario mapping
- `deliverables/Test_Cases_PBI_<PBI>.xlsx` - Azure DevOps import-ready test cases
- `logs/00-WORKFLOW-SUMMARY.md` - Complete workflow report

**Checkpoints**:
- After Phase 3: Review QA Understanding Document
- After Phase 4: Review Test Scenario Mapping

## 📊 Excel Output Format

### Test Cases Excel Structure
Based on Azure DevOps Test Case export format:

| Column | Description |
|--------|-------------|
| ID | Test Case ID (auto-generated) |
| Work Item Type | Always "Test Case" |
| Title | Test case title |
| Test Step | Step number (1, 2, 3...) |
| Step Action | Detailed action to perform |
| Step Expected | Expected result |
| Area Path | Azure DevOps area path |
| Assigned To | QA team member |
| State | Design/Ready/Closed |

## 🔧 Configuration

### Azure DevOps MCP
Edit `.mcp.json` to configure Azure DevOps connection:

```json
{
  "mcpServers": {
    "azure-devops": {
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp", "digital-it-apps"],
      "env": {
        "AZURE_DEVOPS_PAT": "${AZURE_DEVOPS_PAT}",
        "ADO_DEFAULT_PROJECT": "NRG-Business-CI"
      }
    }
  }
}
```

### Environment Variables

**IMPORTANT**: Do NOT use `.env` file. Set as Windows environment variable:

```powershell
# PowerShell
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-token', 'User')
```

Restart Claude Code after setting the environment variable.

## 📚 Documentation

- [docs/setup/QUICK_START.md](docs/setup/QUICK_START.md) - Quick reference guide
- [docs/setup/SETUP_GUIDE.md](docs/setup/SETUP_GUIDE.md) - Full environment + MCP setup
- [docs/standards/](docs/standards/) - QA document formatting standards
- [docs/integrations/](docs/integrations/) - Integration documentation
- [archive/history/](archive/history/) - Superseded point-in-time status reports

## 🚀 Usage Examples

### Example 1: Complete Workflow (Recommended)
```bash
@qa-workflow 643243
```

This is the **recommended approach** - runs all 5 phases with user checkpoints.

**Alternative** (same result):
```bash
@qa-workflow-orchestrator 643243
```

### Example 2: Multiple PBIs
```bash
# Process first PBI
@qa-workflow 634367
# Review outputs, then process next PBI
@qa-workflow 643243
```

### Example 3: Manual Step-by-Step (Advanced)
**Note**: Not recommended - use `@qa-workflow` instead. Manual steps shown for reference only.

```bash
# Individual agent invocation is NOT the standard workflow
# Agents are coordinated by the orchestrator, not called directly
# Use @qa-workflow for complete orchestration with checkpoints
```

**Why use `@qa-workflow` instead of individual agents?**
- ✅ Automatic phase coordination
- ✅ Built-in validation between phases
- ✅ User checkpoints for review
- ✅ Error handling and resume capability
- ✅ Final workflow summary report
- ✅ Guaranteed output consistency

## 🔍 Integration Documentation

Integration documentation is stored in `docs/integrations/` with the following structure:

### API Documentation
- **Location**: `docs/integrations/apis/`
- **Format**: Markdown files describing API endpoints
- **Sections**:
  - Description
  - HTTP Method
  - Path/Query Parameters
  - Request/Response schemas
  - Error scenarios
  - Example usage

### Database Documentation
- **Location**: `docs/integrations/database/`
- **Format**: Markdown files describing database schemas
- **Sections**:
  - Table schemas
  - Relationships
  - Constraints
  - Sample queries

### Business Logic Documentation
- **Location**: `docs/integrations/business-logic/`
- **Format**: Markdown files describing business rules
- **Sections**:
  - Validation rules
  - Calculation logic
  - Business constraints
  - Edge cases

## 🆘 Troubleshooting

### Azure DevOps PAT Not Found
```powershell
# Check if environment variable is set (PowerShell)
$env:AZURE_DEVOPS_PAT

# If not set, set it as Windows environment variable
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-token', 'User')

# Restart Claude Code to pick up the variable
```

**Note**: Do NOT use `.env` file. The PAT must be a Windows OS environment variable.

### MCP Connection Failed
1. Verify `.mcp.json` configuration
2. Restart Claude Code session
3. Check MCP server logs

### No Integration Documentation Found
1. Verify MD files exist in `docs/integrations/`
2. Check file paths in agent prompts
3. Review `md_file_reader` agent logs

## 📝 Contributing

To add new integration documentation:
1. Create MD file in appropriate `docs/integrations/` subdirectory
2. Follow existing documentation format
3. Include all required sections
4. Update this README if needed

## 📄 License

Internal NRG project - not for external distribution.

## 🔗 Related Projects

- [usage-empire](../usage-empire/) - Main Usage Empire codebase
- Parent MCP server implementation

---

## 📌 Quick Reference

**Command**: `@qa-workflow <PBI_NUMBER>`

**Example**: `@qa-workflow 643243`

**Output Directory**: `outputs/<PBI_NUMBER>/deliverables/`

**Deliverables**:
1. `deliverables/QA_Understanding_Document.docx` - Professional Word document
2. `deliverables/Test-Scenarios-Mapped-to-AC.xlsx` - Scenario mapping
3. `deliverables/Test_Cases_PBI_<PBI>.xlsx` - Azure DevOps import-ready test cases
4. `logs/00-WORKFLOW-SUMMARY.md` - Workflow summary

**User Checkpoints**: 2 (after QA doc, after scenario mapping)

---

**Version**: 2.0.0  
**Last Updated**: 2026-08-21  
**Status**: Production-Ready
