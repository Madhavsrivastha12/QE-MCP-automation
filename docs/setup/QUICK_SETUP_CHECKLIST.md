# QA Agent Setup - Quick Checklist

Use this as a quick reference while following the complete setup guide.

---

## ☐ Phase 1: Software Installation

```bash
# Verify installations:
git --version          # Expected: 2.40+
node --version         # Expected: v18+
npm --version          # Expected: 9+
python --version       # Expected: 3.10+
```

---

## ☐ Phase 2: Project Setup

```bash
# Extract to:
C:\UE_Automation\QE_MCP_automation\

# Install dependencies:
cd /c/UE_Automation/QE_MCP_automation
python -m pip install python-docx openpyxl
npm install

# Verify:
python -c "import docx; import openpyxl; print('Success')"
ls -la .claude/agents/  # Should show 10+ agent .md files
```

---

## ☐ Phase 3: Claude Code

```bash
# Install Google Cloud SDK
gcloud init
gcloud auth list  # Should show ACTIVE

# VS Code:
# - Install Claude Code extension
# - Sign in (Command Palette: "Claude Code: Sign In")
# - Verify: Should show "Connected"
```

---

## ☐ Phase 4: Azure DevOps PAT

**Create PAT**:
1. https://dev.azure.com/digital-it-apps
2. Profile → Personal Access Tokens → + New Token
3. Scopes: Work Items (R/W), Code (R), Test Management (R/W), Build (R)
4. Copy token immediately

**Set Environment Variable** (PowerShell):
```powershell
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-token', 'User')
[System.Environment]::GetEnvironmentVariable('AZURE_DEVOPS_PAT', 'User')
```

**RESTART**: Close all terminals, VS Code, reopen

**Verify** (Git Bash):
```bash
echo $AZURE_DEVOPS_PAT  # Should show 52-character token
```

---

## ☐ Phase 5: MCP Verification

```bash
# Test Azure DevOps MCP
npx -y @azure-devops/mcp digital-it-apps --help
# Should show help text

# In Claude Code:
# Type: List available agents
# Expected: ado-pbi-fetcher, qa-workflow-orchestrator, ui-test-executor, etc.
```

---

## ☐ Phase 6: End-to-End Test

```bash
# In Claude Code:
@qa-workflow 643243

# Expected workflow:
# 1. Fetches PBI
# 2. Asks for test type and component
# 3. Creates user-context.json
# 4. Generates QA_Understanding_Document.docx
# 5. Generates Test-Scenarios-Mapped-to-AC.xlsx
# 6. Generates Test_Cases_PBI_643243.xlsx
# 7. All files in outputs/643243/
```

---

## ✅ Success Indicators

- [ ] All software versions verified
- [ ] Python packages installed (python-docx, openpyxl)
- [ ] Node packages installed (exceljs)
- [ ] Claude Code connected in VS Code
- [ ] gcloud authenticated
- [ ] AZURE_DEVOPS_PAT set and persists after restart
- [ ] Azure DevOps MCP responds to --help
- [ ] List agents shows 8+ agents
- [ ] @qa-workflow runs successfully
- [ ] Output files generated in outputs/<PBI>/

---

## 🚨 Common Issues

| Problem | Quick Fix |
|---------|-----------|
| PAT not found | Restart VS Code and all terminals after setting env var |
| MCP not connected | Verify `echo $AZURE_DEVOPS_PAT` shows token |
| Module not found | `python -m pip install python-docx openpyxl` |
| Git Bash not found | Install Git for Windows, restart VS Code |
| Vertex AI timeout | `gcloud auth list` should show ACTIVE |

---

## 📖 Full Documentation

For detailed instructions, troubleshooting, and security:

**Open**: `DB_UI_API_AGENT_SETUP_GUIDE.docx`

**Sections**:
- Section 4: Step-by-step installation
- Section 12: Complete validation checklist  
- Section 13: Detailed troubleshooting
- Section 14: Security best practices

---

## 🎯 First Workflow

```bash
# In Claude Code:
@qa-workflow <PBI_NUMBER>

# Example:
@qa-workflow 643243

# When prompted:
# 1. Select test type (API/UI/Database/Mixed)
# 2. Provide component details
# 3. Add any additional context
# 4. Review and approve at checkpoints
```

---

**Quick Setup Status**: ☐ Not Started | ⚙️ In Progress | ✅ Complete
