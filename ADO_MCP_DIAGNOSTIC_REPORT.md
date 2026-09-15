# Azure DevOps MCP Connectivity Diagnostic Report

**Date**: 2026-09-15  
**Issue**: Azure DevOps MCP server timeout / unable to fetch work items  
**Severity**: BLOCKING — prevents end-to-end QA workflow testing

---

## Root Cause

**Azure DevOps Personal Access Token (PAT) Authentication Failure**

The PAT stored in the `AZURE_DEVOPS_PAT` environment variable is being **rejected by Azure DevOps** with HTTP 401 Unauthorized.

### Evidence

1. **Direct REST API Test Result**:
   ```
   Organization: digital-it-apps
   Project: NRG-Business-CI
   Work Item ID: 643243
   
   HTTP Status: 401
   ✗ Authentication FAILED - PAT invalid or expired
   ```

2. **MCP Tool Test Result**:
   ```
   mcp__azure-devops__wit_work_item → timeout (1800s)
   Error: "sent no response or progress for 1800s"
   ```

3. **PAT Configuration Check**:
   ```
   ✓ User-level PAT exists (length: 84 chars)
   ✓ Process environment has PAT (length: 84 chars)
   ⚠ Format: 84 alphanumeric characters (unusual length)
   ⚠ Contains uppercase characters
   ```

### Why This Causes MCP Timeout

The Azure DevOps MCP server (`@azure-devops/mcp`) uses the `AZURE_DEVOPS_PAT` to authenticate API calls. When authentication fails:

1. MCP server starts successfully (logged: "Starting Azure DevOps MCP Server")
2. Tool calls are received and forwarded to Azure DevOps REST API
3. Azure DevOps rejects the request with 401 Unauthorized
4. MCP server **hangs** waiting for a response that never completes properly
5. Claude Code times out after 1800 seconds (30 minutes)

---

## Configuration Status

### ✓ Environment Variable

- **Location**: User-level environment variable
- **Variable Name**: `AZURE_DEVOPS_PAT`
- **Status**: ✓ SET (present in environment)
- **Length**: 84 characters
- **Format**: Alphanumeric with uppercase (atypical for Azure DevOps PAT)

### ✓ MCP Server Configuration

**File**: `.mcp.json`

```json
{
  "mcpServers": {
    "azure-devops": {
      "command": "npx",
      "args": [
        "-y",
        "@azure-devops/mcp",
        "digital-it-apps"
      ],
      "env": {
        "AZURE_DEVOPS_PAT": "${AZURE_DEVOPS_PAT}",
        "ADO_DEFAULT_PROJECT": "NRG-Business-CI"
      }
    }
  }
}
```

**Status**: ✓ CORRECT
- Organization: `digital-it-apps`
- Default Project: `NRG-Business-CI`
- PAT substitution: `${AZURE_DEVOPS_PAT}` properly configured
- Command: `npx -y @azure-devops/mcp` (available, version 2.10.0)

### ✓ Dependencies

- **npx**: ✓ Available (version 10.9.2)
- **@azure-devops/mcp**: ✓ Available (can be invoked via `npx -y`)
- **Node.js**: ✓ Functional

### ✗ Authentication

- **Status**: ✗ FAILING
- **Error**: HTTP 401 Unauthorized
- **Likely Causes**:
  1. **PAT has expired** (most common)
  2. PAT was revoked or regenerated
  3. PAT doesn't have required scopes for the organization
  4. PAT is for a different Azure DevOps organization

---

## Required Actions

### ACTION REQUIRED: Regenerate Azure DevOps PAT

The user must create a new Personal Access Token in Azure DevOps.

#### Step 1: Create New PAT

1. Navigate to: https://dev.azure.com/digital-it-apps
2. Click User Settings (top-right) → Personal Access Tokens
3. Click **+ New Token**
4. Configure:
   - **Name**: `QE_MCP_Automation` (or any descriptive name)
   - **Organization**: `digital-it-apps`
   - **Expiration**: 90 days (or longer)
   - **Scopes**: **Custom defined**, select:
     - ✓ **Work Items**: Read, Write, & Manage
     - ✓ **Code**: Read
     - ✓ **Test Management**: Read & Write
     - ✓ **Build**: Read
5. Click **Create**
6. **IMPORTANT**: Copy the token immediately (you won't be able to see it again)

#### Step 2: Update Environment Variable

**PowerShell (run as current user, NOT Administrator)**:

```powershell
# Replace 'your-new-pat-token-here' with the actual PAT from Step 1
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-new-pat-token-here', 'User')
```

**Verify it was set**:

```powershell
# Should show the first 4 characters + "..."
$pat = [System.Environment]::GetEnvironmentVariable('AZURE_DEVOPS_PAT', 'User')
if ($pat) {
    Write-Host "✓ PAT updated successfully"
    Write-Host "  Preview: $($pat.Substring(0, 4))..."
} else {
    Write-Host "✗ PAT not set"
}
```

#### Step 3: Restart Claude Code

**CRITICAL**: You MUST restart Claude Code for it to pick up the new environment variable.

1. Exit Claude Code completely
2. Close all terminal windows
3. Re-launch Claude Code
4. The new PAT will be available

#### Step 4: Verify Connectivity

After restarting Claude Code, run this PowerShell test:

```powershell
$org = "digital-it-apps"
$project = "NRG-Business-CI"
$workItemId = "643243"

$pat = $env:AZURE_DEVOPS_PAT
if (-not $pat) {
    Write-Host "ERROR: AZURE_DEVOPS_PAT not set"
    exit 1
}

$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes((":$pat")))
$headers = @{ Authorization = "Basic $base64AuthInfo" }
$url = "https://dev.azure.com/$org/$project/_apis/wit/workitems/${workItemId}?api-version=7.0"

try {
    $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get
    Write-Host "✓ PAT Authentication SUCCESSFUL" -ForegroundColor Green
    Write-Host "Work Item Title:" $response.fields."System.Title"
} catch {
    Write-Host "✗ Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
}
```

**Expected Output**:
```
✓ PAT Authentication SUCCESSFUL
Work Item Title: [The actual work item title]
```

---

## Alternative: Use Interactive Authentication (NOT RECOMMENDED)

If regenerating the PAT is not immediately possible, you could modify `.mcp.json` to use interactive authentication (browser popup), but this is **NOT recommended for automation**:

```json
{
  "mcpServers": {
    "azure-devops": {
      "command": "npx",
      "args": [
        "-y",
        "@azure-devops/mcp",
        "digital-it-apps",
        "--authentication", "interactive"
      ],
      "env": {
        "ADO_DEFAULT_PROJECT": "NRG-Business-CI"
      }
    }
  }
}
```

**Drawback**: Requires manual browser authentication on every Claude Code restart.

---

## What Was NOT Changed

✓ Existing `AZURE_DEVOPS_PAT` environment variable was **not modified or deleted**  
✓ `.mcp.json` configuration was **not changed**  
✓ QA workflow logic was **not modified**  
✓ Output structure was **not changed**  
✓ No destructive changes were made  

---

## Post-Fix Verification Checklist

After updating the PAT and restarting Claude Code:

- [ ] PowerShell test shows `✓ PAT Authentication SUCCESSFUL`
- [ ] MCP tool call succeeds: `mcp__azure-devops__wit_work_item` returns work item data
- [ ] Can fetch PBI 643243 or any other work item
- [ ] Ready for end-to-end QA workflow test

---

## Next Steps

1. **User**: Create new Azure DevOps PAT (5 minutes)
2. **User**: Update `AZURE_DEVOPS_PAT` environment variable via PowerShell
3. **User**: Restart Claude Code
4. **User**: Notify me when ready
5. **Claude**: Run lightweight MCP connectivity test
6. **Claude**: If successful, proceed with fresh end-to-end QA workflow test on a known PBI

---

## Additional Context

### Typical Azure DevOps PAT Format

- **Length**: 52 characters (most common)
- **Format**: Lowercase alphanumeric only (`[a-z0-9]{52}`)
- **Example** (fake): `6kbzw5h2x3y4t5m6n7p8q9r0s1a2b3c4d5e6f7g8h9i0j1k2`

The current PAT has **84 characters** and **contains uppercase**, which is atypical. This suggests it may be:
- A newer format (Azure DevOps has introduced longer PATs)
- Or possibly corrupted/incomplete during initial setup

Regardless, the HTTP 401 response confirms it's not authenticating successfully.

### Why MCP Timeout Happens

The MCP server doesn't fail fast on auth errors. Instead:
1. It forwards the request to Azure DevOps
2. Azure DevOps returns 401 (rejected)
3. MCP server waits for a successful response that never comes
4. Claude Code times out after 1800 seconds (30 minutes)

This is a known behavior with MCP servers that don't have proper error handling for authentication failures.

### Future Prevention

Consider setting a custom timeout in `.mcp.json` for the Azure DevOps MCP server to fail faster:

```json
{
  "mcpServers": {
    "azure-devops": {
      "command": "npx",
      "args": [...],
      "env": {...},
      "timeout": 30000
    }
  }
}
```

This would fail after 30 seconds instead of 30 minutes, making debugging easier.

---

**STATUS**: ⏸️ **BLOCKED** — Waiting for user to regenerate Azure DevOps PAT and update environment variable
