# MCP Configuration Setup Guide

## Overview

This QA automation project uses MCP (Model Context Protocol) servers to interact with:
1. **Azure DevOps** - For fetching PBIs, test cases, and work items
2. **Usage Empire Dev** - For accessing development environment APIs and data
3. **Postgres** - For direct database queries against the dev environment

**IMPORTANT**: 
- This project references MCP server code and credentials from `c:\UE_Automation\usage-empire`
- **No duplication** of code or credentials is needed in this automation project
- **No `.env` files** - All credentials use Windows OS environment variables
- Credentials are NEVER stored in files, only in Windows user environment

## Prerequisites

### 1. Usage Empire Repository
Ensure the usage-empire repository exists at:
```
c:\UE_Automation\usage-empire
```

### 2. Google Cloud Credentials
The MCP servers require Google Cloud service account credentials. These files should be placed in the usage-empire repository (NOT in this QE automation project):

```
c:\UE_Automation\usage-empire\.nrg\keys\dev.json
```

**To obtain credentials:**
- Contact your GCP admin or DevOps team
- Or download from Google Cloud Console → IAM & Admin → Service Accounts
- The service account needs access to:
  - Cloud Run services
  - BigQuery datasets
  - Cloud SQL instances
  - GCS buckets

### 3. Azure DevOps Personal Access Token (PAT)
Set the `AZURE_DEVOPS_PAT` as a **Windows OS user environment variable**.

**IMPORTANT**: This project does NOT use `.env` files. All credentials come from Windows environment variables.

**See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for complete setup instructions.**

**Quick Setup (PowerShell - Recommended):**
```powershell
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-pat-token', 'User')
```

**After setting**: Restart your terminal/Claude Code session.

**To create a PAT:**
1. Go to Azure DevOps → User Settings → Personal Access Tokens
2. Create new token with scopes: Work Items (Read, Write), Code (Read), Test Management (Read, Write)
3. Copy the token immediately (it won't be shown again)
4. Set as Windows environment variable (not in any file)

## MCP Configuration

The `.mcp.json` file in this project references paths in the usage-empire repository using absolute Windows paths:

```json
{
  "mcpServers": {
    "usage-empire-dev": {
      "command": "uv",
      "args": [
        "--directory",
        "c:\\UE_Automation\\usage-empire\\ue-api",
        "run",
        "src/mcp/server.py",
        "--env",
        "env/dev.yml"
      ],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "c:\\UE_Automation\\usage-empire\\.nrg\\keys\\dev.json"
      }
    }
  }
}
```

## Verification Steps

### 1. Check Directory Structure
```bash
# Verify usage-empire exists
ls c:\UE_Automation\usage-empire

# Verify ue-api exists
ls c:\UE_Automation\usage-empire\ue-api

# Verify MCP server scripts exist
ls c:\UE_Automation\usage-empire\ue-api\src\mcp
```

Expected output should show `server.py` and `run_postgres_mcp.py`.

### 2. Check Credentials
```bash
# Verify credentials directory exists
ls c:\UE_Automation\usage-empire\.nrg\keys

# Check if dev.json exists (file should exist but won't show content)
test -f c:\UE_Automation\usage-empire\.nrg\keys\dev.json && echo "✓ Credentials found" || echo "✗ Missing dev.json"
```

### 3. Check Environment Variables
```bash
# Check Azure DevOps PAT
printenv AZURE_DEVOPS_PAT
```

If the variable is not set, restart your terminal or set it using the commands above.

### 4. Test MCP Connection
From Claude Code, run:
```
/mcp
```

Expected output:
- **azure-devops**: Connected ✓
- **usage-empire-dev**: Connected ✓ (requires dev.json)
- **postgres**: Connected ✓ (requires dev.json)

## Troubleshooting

### "usage-empire-dev: not connected"
**Cause**: Missing Google Cloud credentials file
**Solution**: 
1. Verify file exists: `c:\UE_Automation\usage-empire\.nrg\keys\dev.json`
2. If missing, obtain credentials from GCP admin
3. Ensure the service account has required permissions

### "postgres: not connected"
**Cause**: Same as usage-empire-dev (shares same credentials)
**Solution**: Follow steps above

### "azure-devops: not connected"
**Cause**: Missing or invalid `AZURE_DEVOPS_PAT` environment variable
**Solution**:
1. Check if variable is set: `printenv AZURE_DEVOPS_PAT`
2. If missing, create/set PAT using commands in Prerequisites section
3. Restart terminal/Claude Code session

### "uv: command not found"
**Cause**: UV package manager not installed
**Solution**:
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or on Windows with PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Path Issues on Windows
If using Git Bash, you may need to convert Windows paths:
- Windows: `c:\UE_Automation\usage-empire`
- Git Bash: `/c/UE_Automation/usage-empire`

The `.mcp.json` uses Windows-style paths with escaped backslashes (`\\`).

## Security Notes

**DO NOT**:
- Commit `dev.json` or any credential files to git
- Share your Azure DevOps PAT with anyone
- Store credentials in files (no `.env`, `.env.local`, etc.)
- Hardcode credentials in code or configuration files
- Store PAT tokens in this QE automation project

**DO**:
- Keep Google Cloud credentials in `usage-empire/.nrg/keys/` directory (gitignored)
- Store `AZURE_DEVOPS_PAT` in **Windows OS user environment variables** only
- Rotate PAT tokens periodically (every 30-90 days)
- Use service accounts with minimal required permissions
- Use `.gitignore` to prevent accidental credential commits
- See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for proper credential management

## What This Project Does NOT Need

- ❌ No `.env`, `.env.local`, `.env.example`, or any environment files
- ❌ No duplicate `ue-api` code
- ❌ No credential JSON files (Google Cloud keys)
- ❌ No environment YAML files (`dev.yml`, `qa.yml`, etc.)
- ❌ No hardcoded credentials anywhere in the codebase

**Why?**
- MCP server code exists in `usage-empire` repository (referenced via absolute paths)
- Google Cloud credentials exist in `usage-empire/.nrg/keys/` (referenced via absolute paths)
- Azure DevOps PAT stored in **Windows OS user environment variables** (not in files)
- Environment configs exist in `usage-empire/ue-api/env/` (referenced via absolute paths)

## What This Project DOES Have

- ✓ `.mcp.json` with absolute path references to usage-empire
- ✓ QA-specific agents for test automation  
- ✓ Python scripts for test case generation
- ✓ Test documentation and templates
- ✓ Setup guides:
  - [README_MCP_SETUP.md](README_MCP_SETUP.md) - MCP configuration guide
  - [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) - Windows environment variable setup
  - [MCP_SETUP_STATUS.md](../../archive/history/MCP_SETUP_STATUS.md) - Current status and next steps
  - [validate_mcp_setup.sh](../../scripts/validate_mcp_setup.sh) - Validation script
