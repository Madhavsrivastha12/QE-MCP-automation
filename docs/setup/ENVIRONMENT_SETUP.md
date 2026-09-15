# Environment Variable Setup for MCP Servers

## Overview

This project uses **Windows OS environment variables** for sensitive credentials. 

**IMPORTANT**: 
- ❌ **NO** `.env` files should exist in this repository
- ❌ **NO** hardcoded credentials in any files
- ✅ All credentials come from **Windows OS environment variables**

## Required Environment Variables

### AZURE_DEVOPS_PAT

**Purpose**: Authentication for Azure DevOps MCP server  
**Used by**: `azure-devops` MCP server  
**Scope**: User-level environment variable (persists across sessions)

## Setup Instructions

### Option 1: PowerShell (Recommended)

Open PowerShell as **regular user** (admin not required):

```powershell
# Set user-level environment variable (persists across sessions)
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-actual-pat-token-here', 'User')

# Verify it was set
[System.Environment]::GetEnvironmentVariable('AZURE_DEVOPS_PAT', 'User')
```

**After setting**: 
- Restart any open terminals/applications
- Restart Claude Code/VS Code
- New processes will inherit the environment variable

### Option 2: Windows System Properties GUI

1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to **Advanced** tab → **Environment Variables**
3. Under **User variables** (top section), click **New**
4. Variable name: `AZURE_DEVOPS_PAT`
5. Variable value: `your-actual-pat-token-here`
6. Click **OK** on all dialogs
7. Restart terminals/applications

### Option 3: Command Prompt

Open Command Prompt as **regular user**:

```cmd
setx AZURE_DEVOPS_PAT "your-actual-pat-token-here"
```

**After setting**: Restart terminals/applications

### Option 4: Git Bash (Temporary - Current Session Only)

```bash
export AZURE_DEVOPS_PAT='your-actual-pat-token-here'
```

**Note**: This only sets the variable for the current session. Use PowerShell or GUI for permanent setup.

## Creating an Azure DevOps Personal Access Token (PAT)

If you don't have a PAT yet:

1. Go to [Azure DevOps](https://dev.azure.com/digital-it-apps)
2. Click your profile icon (top right) → **Personal Access Tokens**
3. Click **+ New Token**
4. Configure:
   - **Name**: `Claude Code MCP - QE Automation`
   - **Organization**: `digital-it-apps`
   - **Expiration**: 90 days (or as per your policy)
   - **Scopes**: Custom defined
     - ✅ **Work Items**: Read & Write
     - ✅ **Code**: Read
     - ✅ **Test Management**: Read & Write
     - ✅ **Build**: Read (for pipeline info)
5. Click **Create**
6. **COPY THE TOKEN IMMEDIATELY** - it's only shown once!
7. Use the token in the environment variable setup above

## Verifying Environment Variable

### Check if Variable is Set

**PowerShell**:
```powershell
# Check user-level variable
[System.Environment]::GetEnvironmentVariable('AZURE_DEVOPS_PAT', 'User')

# Check current process environment
$env:AZURE_DEVOPS_PAT
```

**Command Prompt**:
```cmd
echo %AZURE_DEVOPS_PAT%
```

**Git Bash**:
```bash
printenv AZURE_DEVOPS_PAT
# or
echo $AZURE_DEVOPS_PAT
```

### Expected Output
- **If set correctly**: Shows the PAT token value
- **If not set**: Empty/blank output or "AZURE_DEVOPS_PAT" (literal text)

### Test MCP Connection

After setting the environment variable and restarting terminals:

```bash
# Run validation script
./scripts/validate_mcp_setup.sh
```

Expected output:
```
✓ AZURE_DEVOPS_PAT is set
  PAT length: 52 characters
```

Or test in Claude Code:
```
/mcp
```

Expected:
```
azure-devops: Connected ✓
```

## Troubleshooting

### "AZURE_DEVOPS_PAT environment variable NOT set"

**Cause**: Variable not set or not visible to current process

**Solutions**:
1. Verify variable is set (see "Verifying" section above)
2. **Restart the application** that needs to read it:
   - Close and reopen terminal/Git Bash
   - Restart VS Code/Claude Code
   - Restart the IDE completely
3. If using PowerShell, ensure you used `'User'` target (not `'Process'`):
   ```powershell
   [System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-token', 'User')
   ```
4. Try setting via Windows GUI (System Properties method)

### "azure-devops: not connected" in /mcp

**Possible causes**:
1. Environment variable not set or not visible
2. PAT token expired or invalid
3. PAT token doesn't have required scopes
4. Network/proxy issues

**Solutions**:
1. Verify variable: `printenv AZURE_DEVOPS_PAT`
2. Check PAT hasn't expired in Azure DevOps
3. Verify PAT has Work Items + Code + Test Management scopes
4. Try recreating the PAT with correct scopes

### Variable Set but Still Not Working

**Windows environment variable precedence**:
1. Process environment (temporary)
2. User environment variables
3. System environment variables

After setting a user-level variable:
- **Restart the terminal/IDE** - new processes inherit the variable
- Do NOT set `AZURE_DEVOPS_PAT` in `.env` or any config file
- The `.mcp.json` uses `${AZURE_DEVOPS_PAT}` syntax which reads from OS environment

### Testing PAT Token Manually

Verify your PAT works:

```bash
# Test Azure DevOps API access
curl -u ":$AZURE_DEVOPS_PAT" \
  "https://dev.azure.com/digital-it-apps/_apis/projects?api-version=7.1"
```

Expected: JSON response with project list  
If error: PAT is invalid or doesn't have required permissions

## Security Best Practices

### ✅ DO
- Store PAT in Windows user environment variables
- Use minimum required scopes when creating PAT
- Set reasonable expiration dates (30-90 days)
- Rotate PAT tokens regularly
- Keep PAT tokens confidential
- Use `.gitignore` to prevent `.env` files from being committed

### ❌ DO NOT
- Commit PAT tokens to git repositories
- Share PAT tokens with others
- Store PAT in `.env` files (this project doesn't use them)
- Use PAT tokens with "Full access" scope
- Store PAT in code, scripts, or configuration files
- Set PAT as a system-wide variable (use user-level)

## How MCP Configuration Uses Environment Variables

The [.mcp.json](../../.mcp.json) file references the environment variable:

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

**How it works**:
1. `${AZURE_DEVOPS_PAT}` is a variable substitution syntax
2. When MCP server starts, it reads from Windows OS environment
3. The value is passed to the `azure-devops` MCP server process
4. **No .env file is needed or used**

## Environment Variable Architecture

```
Windows OS User Environment
    ↓
AZURE_DEVOPS_PAT=<your-token>
    ↓
Claude Code Process (inherits environment)
    ↓
.mcp.json reads ${AZURE_DEVOPS_PAT}
    ↓
azure-devops MCP server receives the value
    ↓
Connects to Azure DevOps API
```

## Related Files

- [.mcp.json](../../.mcp.json) - MCP server configuration (uses `${AZURE_DEVOPS_PAT}`)
- [.gitignore](../../.gitignore) - Ensures no `.env` files are committed
- [validate_mcp_setup.sh](../../scripts/validate_mcp_setup.sh) - Checks environment variable is set
- [MCP_SETUP_STATUS.md](../../archive/history/MCP_SETUP_STATUS.md) - Overall setup status
- [README_MCP_SETUP.md](README_MCP_SETUP.md) - Complete MCP setup guide

## Summary

✅ **This project DOES**:
- Use Windows OS user environment variables for `AZURE_DEVOPS_PAT`
- Read environment variables via `${VARIABLE}` syntax in `.mcp.json`
- Gitignore `.env` files to prevent accidental commits

❌ **This project DOES NOT**:
- Use `.env` files
- Store credentials in files
- Require any `.env.local` or `.env.example` files
- Load environment variables from files at runtime

All credential management is handled by **Windows OS environment variables** for security and portability.
