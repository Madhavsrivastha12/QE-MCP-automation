# .agents Directory

This directory contains configuration templates for Claude Code and MCP servers that are copied to the root directory during setup.

## Files

- **mcp_config.json** - Template for `.mcp.json` (MCP server configuration)
- **skills/** - Custom Claude Code skills (copied to `.claude/skills/`)

## Setup

Run the setup script to copy configurations to their proper locations:

```bash
bash setup_claude_mcp.sh
```

This script will:
1. Copy `.agents/mcp_config.json` → `.mcp.json`
2. Copy `.agents/skills/*` → `.claude/skills/`

## Important Notes

### Environment Variables

The `.mcp.json` file uses environment variables for sensitive data. You must create a `.env.mcp` file in the root directory with:

```bash
# Copy .env.mcp.example to .env.mcp and fill in your values
cp .env.mcp.example .env.mcp
```

### Git Ignore

- `.mcp.json` is ignored by git (generated from template)
- `.env.mcp` is ignored by git (contains secrets)
- `.mcp.json.example` and `.env.mcp.example` are committed as templates

### Updating MCP Configuration

1. Edit `.agents/mcp_config.json` (the source template)
2. Run `bash setup_claude_mcp.sh` to regenerate `.mcp.json`
3. Restart Claude Code session

**Do NOT manually edit `.mcp.json`** - edit the template instead!
