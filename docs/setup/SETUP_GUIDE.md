# QA Agent Flow - Setup Guide

**Quick setup guide to get your QA testing automation running.**

---

## Prerequisites

- Claude Code installed and configured
- Access to Azure DevOps (NRG-Business-CI project)
- Azure DevOps Personal Access Token (PAT)
- Access to `C:\UE_Automation\usage-empire` (parent repo)

---

## Setup Steps

### Step 1: Configure Azure DevOps PAT Token

1. **Get your Azure DevOps PAT**:
   - Go to Azure DevOps → User Settings → Personal Access Tokens
   - Click "New Token"
   - Name: "Claude Code QA Automation"
   - Scopes: Work Items (Read), Projects (Read)
   - Copy the generated token

2. **Create `.env` file**:
   ```bash
   cd c:\UE_Automation\QE_MCP_automation
   cp .env.example .env
   ```

3. **Add your PAT to `.env`**:
   ```bash
   # Edit .env file
   AZURE_DEVOPS_PAT=your_actual_pat_token_here
   ```

### Step 2: Verify MCP Configuration

The `.mcp.json` file should already be configured. Verify it contains:

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
    },
    "usage-empire-dev": {
      "command": "uv",
      "args": [
        "--directory",
        "../usage-empire/ue-api",
        "run",
        "src/mcp/server.py",
        "--env",
        "env/dev.yml"
      ],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "../usage-empire/.nrg/keys/dev.json"
      }
    }
  }
}
```

### Step 3: Restart Claude Code

**Important**: Agent definitions are only loaded at session start.

1. Close Claude Code completely
2. Reopen Claude Code
3. Verify agents are loaded:
   ```
   Type @ and you should see:
   - @ado-pbi-fetcher
   - @md-file-reader
   - @qa-understanding-doc-creator
   - @test-scenario-ac-mapper
   - @qa-test-cases-generator
   - @qa-workflow-orchestrator
   ```

### Step 4: Create Sample Integration Documentation

If you don't have integration docs yet, the sample API doc is already created:
- `docs/integrations/apis/pod-forecast-batch-results.md`

You can add more documentation files in:
- `docs/integrations/apis/` - API endpoint docs
- `docs/integrations/database/` - Database schema docs
- `docs/integrations/business-logic/` - Business rules docs

### Step 5: Test the Setup

Run a simple test to verify everything works:

```bash
# Test Azure DevOps MCP connection
@ado-pbi-fetcher 643243
```

Expected result:
- Agent runs successfully
- Creates `outputs/643243/working/pbi-data.json`
- JSON contains PBI title, description, acceptance criteria

If this works, you're ready to use the full workflow!

---

## Quick Test: Full Workflow

Run the complete workflow for PBI 643243:

```bash
@qa-workflow-orchestrator 643243
```

**What will happen**:
1. Agent fetches PBI 643243 from Azure DevOps
2. Agent reads integration docs from `docs/integrations/`
3. Agent creates QA Understanding Document
4. **CHECKPOINT**: You review the QA doc and approve
5. Agent maps test scenarios to AC in Excel
6. **CHECKPOINT**: You review scenarios and approve
7. Agent generates detailed test cases in Excel
8. Final report displayed

**Expected outputs** in `outputs/643243/`:
- `pbi-data.json`
- `integration-docs.json`
- `QA_Understanding_Document.md`
- `Test-Scenarios-Mapped-to-AC.xlsx`
- `Test_Cases.xlsx`
- `00-WORKFLOW-SUMMARY.md`

---

## Troubleshooting

### Error: "Azure DevOps MCP tools not found"

**Solution**:
1. Verify `.env` file exists with `AZURE_DEVOPS_PAT` set
2. Restart Claude Code session
3. Check `.mcp.json` has `azure-devops` server configured

### Error: "No integration docs found"

**Solution**:
1. Create MD files in `docs/integrations/apis/`
2. Or the workflow will proceed with PBI data only (with warning)

### Error: "openpyxl module not found"

**Solution**:
```bash
cd ../usage-empire/ue-api
uv pip install openpyxl
```

### Agents Not Showing in @ Menu

**Solution**:
1. Restart Claude Code completely
2. Verify agent files exist in `.claude/agents/`
3. Check agent YAML frontmatter is valid

---

## Directory Structure After Setup

```
QE_MCP_automation/
├── .claude/
│   └── agents/
│       ├── ado_pbi_fetcher.md              ✅
│       ├── md_file_reader.md               ✅
│       ├── qa_understanding_doc_creator.md ✅
│       ├── test_scenario_ac_mapper.md      ✅
│       ├── qa_test_cases_generator.md      ✅
│       └── qa_workflow_orchestrator.md     ✅
│
├── docs/
│   └── integrations/
│       ├── apis/
│       │   └── pod-forecast-batch-results.md  ✅
│       ├── database/                       📁
│       └── business-logic/                 📁
│
├── outputs/                                📁 (will be created)
│
├── .env                                    ✅ (you created)
├── .env.example                            ✅
├── .gitignore                              ✅
├── .mcp.json                               ✅
├── IMPLEMENTATION_PLAN.md                  ✅
├── PROGRESS_STATUS.md                      ✅
├── QUICK_START.md                          ✅
├── README.md                               ✅
└── SETUP_GUIDE.md                          ✅ (this file)
```

---

## Environment Variables Reference

### Required
- `AZURE_DEVOPS_PAT` - Azure DevOps Personal Access Token

### Optional (inherited from usage-empire)
- `GOOGLE_APPLICATION_CREDENTIALS` - GCP service account key path

---

## MCP Servers Used

| Server | Purpose | Required For |
|--------|---------|--------------|
| azure-devops | Fetch PBIs, comments | ADO PBI Fetcher agent |
| usage-empire-dev | Database queries (if needed) | Optional - for test data validation |
| postgres | Direct DB access (if needed) | Optional - for integration test scenarios |

---

## Next Steps After Setup

1. **Test with your own PBI**:
   ```bash
   @qa-workflow-orchestrator <your-pbi-number>
   ```

2. **Add integration documentation**:
   - Create MD files in `docs/integrations/`
   - Follow the template in `pod-forecast-batch-results.md`

3. **Review generated test cases**:
   - Check `outputs/<PBI>/deliverables/Test_Cases_PBI_<PBI>.xlsx`
   - Verify they match your requirements

4. **Import to Azure DevOps**:
   - Use Azure DevOps "Import Test Cases" feature
   - Select the generated Excel file

5. **Customize as needed**:
   - Edit agent prompts in `.claude/agents/`
   - Adjust test case format if needed
   - Add custom validation rules

---

## Support

**Documentation**:
- [IMPLEMENTATION_PLAN.md](../../archive/history/IMPLEMENTATION_PLAN.md) - Complete implementation details
- [README.md](../../README.md) - Project overview
- [QUICK_START.md](QUICK_START.md) - Quick reference

**Common Issues**:
- See "Troubleshooting" section above
- Check [PROGRESS_STATUS.md](../../archive/history/PROGRESS_STATUS.md) for known issues

---

**Setup Complete! 🎉**

You're ready to automate QA test case generation from Azure DevOps PBIs.
