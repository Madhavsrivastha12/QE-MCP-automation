# QA Agent Flow - Quick Start Guide

## 📋 Current Status

**Codebase**: Partially configured from `usage-empire` repo  
**MCP Servers**: Configured and ready (Azure DevOps + PostgreSQL)  
**Agents**: Need to create 6 new agents for QA workflow  

---

## ⚠️ Critical Questions (MUST ANSWER FIRST)

Before implementation can start, I need answers to these questions:

### 1. Azure DevOps MCP
- **Q**: What Azure DevOps MCP package are you using?
  - Is it `@azure-devops/mcp` (npm package)?
  - Or a custom implementation?
- **Q**: What's your Azure DevOps PAT token environment variable name?
  - Currently configured as `AZURE_DEVOPS_PAT`
- **Q**: Provide 2-3 sample PBI numbers for testing
  - Example: 643243 (from your diagram)

### 2. MD Documentation Files
- **Q**: Where are your integration MD files stored?
  - Separate repository?
  - In `C:\UE_Automation\usage-empire` somewhere?
  - Azure DevOps wiki?
- **Q**: Can you provide a sample MD file or describe the format?
  - What sections does it contain?
  - Example: API endpoint docs for `/pod-forecast-batch-results`

### 3. Excel Output Format
- **Q**: Do you have a template for `Test-Scenarios-Mapped-to-AC-CustomForecast.xls`?
  - Can you share a sample?
- **Q**: What columns are mandatory vs optional?

### 4. File Structure
- **Q**: Should this project reference MCP server from `../usage-empire/`?
  - Or copy the entire `ue-api` folder here?
- **Q**: Should QE_MCP_automation be fully standalone?

---

## 🎯 What Will Be Built

### Agent Flow (5 Agents + 1 Orchestrator)

```
1. ADO PBI Fetcher Agent
   ├─ Input: PBI number (e.g., 643243)
   ├─ Action: Fetch from Azure DevOps
   └─ Output: pbi-data.json (Description, AC, Notes, Comments)

2. MD File Reader Agent
   ├─ Input: Path to integration MD files
   ├─ Action: Parse and structure documentation
   └─ Output: integration-docs.json (API, DB, Business Logic)

3. QA Understanding Doc Creator Agent
   ├─ Input: pbi-data.json + integration-docs.json
   ├─ Action: Combine and synthesize
   └─ Output: QA_Understanding_Document.md

4. Test Scenario to AC Mapping Agent
   ├─ Input: QA_Understanding_Document.md
   ├─ Action: Extract scenarios, map to AC
   └─ Output: Test-Scenarios-Mapped-to-AC.xlsx

5. Test Cases Generator Agent
   ├─ Input: QA_Understanding_Document.md + Test-Scenarios-Mapped-to-AC.xlsx
   ├─ Action: Generate detailed test cases
   └─ Output: Test_Cases.xlsx

6. QA Workflow Orchestrator (Coordinates all above)
   ├─ Input: PBI number
   ├─ Action: Run agents 1→2→3→4→5 with checkpoints
   └─ Output: All deliverables in outputs/<PBI>/
```

---

## 📁 Proposed Directory Structure

```
C:\UE_Automation\QE_MCP_automation\
├── .claude/
│   └── agents/
│       ├── ado_pbi_fetcher.md              ← NEW
│       ├── md_file_reader.md               ← NEW  
│       ├── qa_understanding_doc_creator.md ← NEW
│       ├── test_scenario_ac_mapper.md      ← NEW
│       ├── qa_test_cases_generator.md      ← NEW
│       └── qa_workflow_orchestrator.md     ← NEW
│
├── docs/
│   └── integrations/                       ← NEW
│       ├── apis/
│       ├── database/
│       └── business-logic/
│
├── outputs/                                ← NEW (gitignored)
│   └── <PBI-NUMBER>/
│       ├── pbi-data.json
│       ├── integration-docs.json
│       ├── QA_Understanding_Document.md
│       ├── Test-Scenarios-Mapped-to-AC.xlsx
│       └── Test_Cases.xlsx
│
├── .mcp.json                              ← Already exists
├── IMPLEMENTATION_PLAN.md                 ← Detailed plan
├── QUICK_START.md                         ← This file
└── README.md                              ← To be updated
```

---

## 🔧 What Already Works

### ✅ MCP Servers Configured
- `usage-empire-dev` → Database + API access (dev env)
- `usage-empire-qa` → Database + API access (qa env)
- `azure-devops` → Azure DevOps integration
- `postgres` / `postgres-qa` → Direct PostgreSQL access

### ✅ Available MCP Tools (from server.py)
- `execute_sql_query(sql, params)` - Run read-only SQL
- `get_pod_details(pod)` - Get pod information
- `get_forecasts(pod)` - Get forecast data
- `generate_identity_token(audience)` - GCP auth token
- `get_task_logs(task_id)` - Fetch GCP logs
- ... and 4 more tools

### ✅ Existing Agent Examples
- 12 QA manual testing agents (can be adapted)
- BA workflow agents (useful patterns)
- Test case generation agents (can reuse logic)

---

## ❌ What's Missing

### Need to Create
1. **6 new agent definition files** (`.claude/agents/*.md`)
2. **MD documentation repository** (`docs/integrations/`)
3. **Output directory structure** (`outputs/`)
4. **Verification that Azure DevOps MCP has required tools**

### Need to Clarify
1. Azure DevOps MCP tool names and signatures
2. MD file format and location
3. Excel output format requirements
4. File path strategy (reference vs copy)

---

## 📅 Implementation Timeline

| Phase | Duration | What Happens |
|-------|----------|--------------|
| **Phase 1: Foundation** | 3-5 days | Setup MCP tools, create MD docs structure |
| **Phase 2: Agent Development** | 5-7 days | Create 6 agents, test individually |
| **Phase 3: Integration** | 3-4 days | End-to-end testing, fix issues |
| **Phase 4: Deployment** | 2-3 days | Documentation, automation scripts |
| **TOTAL** | **13-19 days** | Depends on user feedback speed |

---

## 🚀 How to Use (After Implementation)

### Simple Mode (One Command)
```bash
# Run entire workflow for PBI 643243
@qa-workflow-orchestrator 643243
```

### Step-by-Step Mode
```bash
# Step 1: Fetch PBI from Azure DevOps
@ado-pbi-fetcher 643243

# Step 2: Read integration documentation
@md-file-reader docs/integrations/apis/custom-forecast.md

# Step 3: Create QA understanding document
@qa-understanding-doc-creator --pbi 643243

# Step 4: Map test scenarios to AC
@test-scenario-ac-mapper outputs/643243/deliverables/QA_Understanding_Document.docx

# Step 5: Generate test cases
@qa-test-cases-generator outputs/643243/
```

---

## 🎬 Next Actions

### For You (User) - Before I Can Start:
1. ✅ Review `IMPLEMENTATION_PLAN.md` 
2. ❓ Answer the 4 critical questions above
3. 📄 Provide sample PBI numbers (2-3 examples)
4. 📄 Provide sample MD file or describe format
5. 📊 Provide sample Excel template (if exists)

### For Me (AI) - After You Answer:
1. Test Azure DevOps MCP and document available tools
2. Create MD documentation structure
3. Create first agent (ADO PBI Fetcher)
4. Test with your sample PBI
5. Proceed with remaining agents

---

## 📝 Notes

### File References Strategy
**Current Plan**: Reference MCP server from parent directory
```json
{
  "mcpServers": {
    "usage-empire-dev": {
      "command": "uv",
      "args": [
        "--directory",
        "../usage-empire/ue-api",  // ← Reference parent repo
        "run",
        "src/mcp/server.py",
        "--env",
        "env/dev.yml"
      ]
    }
  }
}
```

**Alternative**: Copy entire `ue-api` to this project (makes it standalone but duplicates code)

### Agent Checkpoints
**Current Plan**: 2 checkpoints
- Checkpoint 1: After QA Understanding Doc created (user reviews)
- Checkpoint 2: After Test Scenarios mapped (user reviews)

Can add more if needed.

---

## 🆘 Help & Support

- **Detailed Plan**: See [IMPLEMENTATION_PLAN.md](../../archive/history/IMPLEMENTATION_PLAN.md)
- **MCP Tools**: See `MCP_TOOLS_INVENTORY.md` (to be created)
- **Questions**: See "Critical Questions" section above

---

**Status**: ⏸️ **WAITING FOR USER INPUT**

Please review and answer the 4 critical question sections, then we can proceed with implementation!
