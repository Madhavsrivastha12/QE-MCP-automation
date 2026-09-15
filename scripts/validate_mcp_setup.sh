#!/bin/bash
# MCP Setup Validation Script
# Validates that all required paths and dependencies exist in the usage-empire repository

echo "========================================="
echo "MCP Setup Validation for QE Automation"
echo "========================================="
echo ""

ERRORS=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

error() {
    echo -e "${RED}✗ $1${NC}"
    ((ERRORS++))
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
    ((WARNINGS++))
}

info() {
    echo -e "${BLUE}  $1${NC}"
}

header() {
    echo -e "${BLUE}$1${NC}"
}

# Base paths
USAGE_EMPIRE_ROOT="c:/UE_Automation/usage-empire"
UE_API_DIR="$USAGE_EMPIRE_ROOT/ue-api"
CREDENTIALS_PATH="$USAGE_EMPIRE_ROOT/.nrg/keys/dev.json"

header "Checking QE MCP Automation Setup"
echo "This project references files from: $USAGE_EMPIRE_ROOT"
echo ""

# 1. Verify no local .env file (should NOT exist)
header "1. Checking for local .env file (should NOT exist)..."
if [ -f ".env" ]; then
    warning ".env file found in QE automation project"
    info "This project should NOT have a .env file"
    info "All configuration is in usage-empire repository"
else
    success "No local .env file (correct setup)"
fi
echo ""

# 2. Check usage-empire repository exists
header "2. Checking usage-empire repository location..."
if [ -d "$USAGE_EMPIRE_ROOT" ]; then
    success "usage-empire repository found at: $USAGE_EMPIRE_ROOT"
else
    error "usage-empire repository NOT found at: $USAGE_EMPIRE_ROOT"
    info "This is required for MCP servers to function"
    info "Clone from: https://dev.azure.com/digital-it-apps/NRG-Business-CI/_git/usage-empire"
fi
echo ""

# 3. Check ue-api directory
header "3. Checking ue-api directory..."
if [ -d "$UE_API_DIR" ]; then
    success "ue-api directory found"

    # Check MCP server scripts
    if [ -f "$UE_API_DIR/src/mcp/server.py" ]; then
        success "MCP server.py found"
    else
        error "MCP server.py NOT found at: $UE_API_DIR/src/mcp/server.py"
    fi

    if [ -f "$UE_API_DIR/src/mcp/run_postgres_mcp.py" ]; then
        success "MCP run_postgres_mcp.py found"
    else
        error "MCP run_postgres_mcp.py NOT found at: $UE_API_DIR/src/mcp/run_postgres_mcp.py"
    fi
else
    error "ue-api directory NOT found at: $UE_API_DIR"
fi
echo ""

# 4. Check environment configuration files
header "4. Checking environment YAML files in usage-empire..."
if [ -f "$UE_API_DIR/env/dev.yml" ]; then
    success "dev.yml found"
else
    error "dev.yml NOT found at: $UE_API_DIR/env/dev.yml"
    info "Required by usage-empire-dev and postgres MCP servers"
fi
echo ""

# 5. Check credentials (in usage-empire, not local)
header "5. Checking Google Cloud credentials in usage-empire..."
if [ -d "$USAGE_EMPIRE_ROOT/.nrg/keys" ]; then
    success ".nrg/keys directory exists in usage-empire"

    if [ -f "$CREDENTIALS_PATH" ]; then
        success "dev.json credentials found in usage-empire"

        # Optional: Validate JSON structure
        if command -v jq &> /dev/null; then
            if jq empty "$CREDENTIALS_PATH" 2>/dev/null; then
                success "dev.json is valid JSON"
            else
                warning "dev.json may be corrupted or invalid JSON"
            fi
        fi
    else
        error "dev.json NOT found at: $CREDENTIALS_PATH"
        info "Required for usage-empire-dev and postgres MCP servers"
        info "Obtain from GCP admin or Google Cloud Console"
        info "Place in usage-empire repository, NOT in this QE project"
    fi
else
    error ".nrg/keys directory NOT found in usage-empire"
fi
echo ""

# 6. Check Azure DevOps PAT (required by azure-devops MCP server)
header "6. Checking Azure DevOps PAT environment variable..."
if [ -n "$AZURE_DEVOPS_PAT" ]; then
    success "AZURE_DEVOPS_PAT is set (from Windows OS environment)"
    PAT_LENGTH=${#AZURE_DEVOPS_PAT}
    info "PAT length: $PAT_LENGTH characters"
else
    error "AZURE_DEVOPS_PAT environment variable NOT set"
    info "Required by azure-devops MCP server"
    info "This must be a Windows OS user environment variable (NOT from .env file)"
    info ""
    info "PowerShell (Recommended):"
    info "  [System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-token', 'User')"
    info ""
    info "See ENVIRONMENT_SETUP.md for complete setup instructions"
    info "Create PAT at: Azure DevOps → User Settings → Personal Access Tokens"
fi
echo ""

# 7. Check UV package manager
header "7. Checking UV package manager..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>&1 | head -1)
    success "UV is installed: $UV_VERSION"
else
    error "UV package manager NOT found"
    info "Required for usage-empire-dev and postgres MCP servers"
    info "Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    info "Or Windows: powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\""
fi
echo ""

# 8. Check npx (for azure-devops MCP server)
header "8. Checking npx (Node Package Runner)..."
if command -v npx &> /dev/null; then
    NPX_VERSION=$(npx --version)
    success "npx is installed: $NPX_VERSION"
else
    error "npx NOT found"
    info "Required by azure-devops MCP server"
    info "Install Node.js from: https://nodejs.org/"
fi
echo ""

# 9. Validate .mcp.json configuration
header "9. Validating .mcp.json configuration..."
if [ -f ".mcp.json" ]; then
    success ".mcp.json found in QE automation project"

    if command -v jq &> /dev/null; then
        if jq empty ".mcp.json" 2>/dev/null; then
            success ".mcp.json is valid JSON"

            # List configured servers
            SERVERS=$(jq -r '.mcpServers | keys[]' ".mcp.json" 2>/dev/null)
            info "Configured MCP servers:"
            echo "$SERVERS" | while read -r server; do
                info "  • $server"
            done

            # Verify paths in .mcp.json point to usage-empire
            UE_PATHS=$(jq -r '.mcpServers | .[] | .args[]? | select(contains("usage-empire"))' ".mcp.json" 2>/dev/null | head -3)
            if [ -n "$UE_PATHS" ]; then
                success "Paths correctly reference usage-empire repository"
            else
                warning "Could not verify paths reference usage-empire"
            fi
        else
            error ".mcp.json is NOT valid JSON"
        fi
    else
        warning "jq not installed - cannot validate .mcp.json structure"
        info "Install jq for detailed validation"
    fi
else
    error ".mcp.json NOT found in current directory"
fi
echo ""

# Summary
echo "========================================="
echo "Validation Summary"
echo "========================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    success "All checks passed! MCP setup is ready."
    echo ""
    info "Next step: Test MCP servers in Claude Code:"
    info "  /mcp"
elif [ $ERRORS -eq 0 ]; then
    warning "Setup complete with $WARNINGS warning(s)"
    info "Warnings may not block functionality - review above"
    echo ""
    info "You can test MCP connection with: /mcp"
else
    error "Found $ERRORS error(s) and $WARNINGS warning(s)"
    info "Fix errors above before using MCP servers"
    echo ""
    info "Common fixes:"
    info "  1. Ensure usage-empire repository is cloned"
    info "  2. Place dev.json in usage-empire/.nrg/keys/"
    info "  3. Set AZURE_DEVOPS_PAT environment variable"
    info "  4. Install UV and npx (Node.js)"
fi
echo ""

exit $ERRORS
