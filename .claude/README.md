# Claude Code Configuration

This directory contains configuration for Claude Code (claude.ai/code).

## Files

### `settings.json` (committed to git)
Project-wide Claude Code settings shared across all developers.

**Current configuration:**
- **Deny rules**: Blocks Claude from reading noisy/sensitive files
  - Build outputs (dist/, build/, node_modules/, .venv/)
  - Generated files (*.pyc, *.min.js, *.map)
  - Large data files (*.csv, *.parquet, *.xlsx)
  - Production configs (env/prod.yml, sqlcode/prod/)
  - Sensitive files (.env, .env.*)
  - IDE/OS files (.DS_Store, .vscode/)

### `settings.local.json` (gitignored)
Developer-specific overrides. Not committed to git.

Create this file to add personal preferences without affecting the team:
```json
{
  "permissions": {
    "deny": [
      "Read(my-local-experiments/**)"
    ]
  }
}
```

### `agents/` directory
Custom agent for the Usage Empire PBI workflow.

#### **orchestrator.md** — All-in-One PBI Implementation Agent

**What it does:**
1. **Phase 1: Planning** — Reads codebase, creates `plans/<PBI-ID>.plan.yaml`
2. **HITL Gate** — Pauses for developer YES approval
3. **Phase 2: Implementation** — Executes all tasks with unit tests
4. **Phase 2: Quality Checks** — Runs tests, lint, coverage (≥80%)
5. **Phase 2: Code Review** — Checks conventions, fixes bugs inline
6. **Phase 3: Security Scan** — Audits code, creates `plans/<PBI-ID>-security.md`
7. **Phase 4: Completion** — Updates plan status, prints summary

---

## How to Implement a PBI

### Step 1: Drop the PBI
Paste your PBI description (any format) and invoke the orchestrator:

```
@"orchestrator (agent)" PBI-12345: Add user authentication endpoint

As a developer
I want a new API endpoint for user authentication
So that users can log in securely

Acceptance Criteria:
- POST /api/v1/auth/login
- Validate email/password
- Return JWT token on success
- Return 401 on failure
```

### Step 2: Review the Plan
The orchestrator will:
1. Read CLAUDE.md for project context
2. Explore the codebase for similar patterns
3. Create `plans/PBI-12345.plan.yaml` with tasks
4. **PAUSE** and show you the plan

You'll see:
```
── PLAN READY ──────────────────────────────────────
Review the plan above.
Type YES to implement, or describe what to change.
────────────────────────────────────────────────────
```

### Step 3: Approve or Revise
- **Type `YES`** (all caps) to proceed with implementation
- **Type changes** if you want the plan revised (e.g., "Use Redis for tokens instead of DB")
- **"ok", "sure", "go ahead" are NOT the same as YES** — orchestrator will ask again

### Step 4: Wait for Implementation
Once you type YES, the orchestrator will:
- Implement each task (code + tests)
- Run quality checks after each task (tests, lint, coverage)
- Fix any issues found during code review
- Run security scan on all modified files
- Create security report: `plans/PBI-12345-security.md`

### Step 5: Review Completion Summary
You'll see:
```
══════════════════════════════════════════════════════
PBI-12345 IMPLEMENTATION COMPLETE
══════════════════════════════════════════════════════

Files created:
  - ue-api/src/ue_fe_api/api/endpoints/auth.py
  - ue-api/tests/test_api/test_auth_endpoints.py

Files modified:
  - ue-api/src/ue_fe_api/api/endpoints/__init__.py

Quality gates:
  ✓ All tests passing
  ✓ Lint clean
  ✓ Coverage ≥80%
  ✓ Code review clean
  ✓ Security scan PASSED

Next steps:
  1. Manual testing in browser/Postman
  2. Create commit: git add . && git commit -m "PBI-12345: Add user auth endpoint"
  3. Create MR/PR for team review
══════════════════════════════════════════════════════
```

### Step 6: Manual Testing & Commit
1. **Test manually**: Start dev server, test the feature in browser/Postman
2. **Create git commit**: Use the suggested commit message
3. **Create MR/PR**: Push to feature branch and create merge request

---

## Important Notes

**After editing `orchestrator.md`**: Restart your Claude Code session for changes to take effect. Agents are loaded only at session start.

**Outputs:**
- `plans/<PBI-ID>.plan.yaml` — Implementation plan
- `plans/<PBI-ID>-security.md` — Security audit report
- Modified/created code files with tests

**If orchestrator gets blocked**: It will stop and report the issue. Fix the blocker (e.g., answer an open question, approve a risky change) and it will continue.

## How File Exclusion Works

Claude Code has two exclusion mechanisms:

### 1. `.gitignore` (automatic)
Claude automatically respects `.gitignore` and excludes those files from context.

### 2. `settings.json` deny rules (explicit)
Hard blocks via `permissions.deny` - Claude **cannot** read these files even if explicitly requested.

**Why both?**
- `.gitignore` = version control + automatic Claude exclusion
- `settings.json` deny rules = security layer for truly sensitive files

## Modifying Deny Rules

To add more files to the deny list:

1. Edit `.claude/settings.json`
2. Add pattern to `permissions.deny` array
3. Patterns use glob syntax: `Read(path/to/file/**)`

Example:
```json
{
  "permissions": {
    "deny": [
      "Read(my-new-folder/**)",
      "Read(**/*.secret)"
    ]
  }
}
```

## Why No `.claudeignore`?

`.claudeignore` doesn't officially exist in Claude Code yet. It's a frequently requested feature but hasn't shipped.

Instead, we use:
- `.gitignore` (already respected by Claude)
- `settings.json` deny rules (official mechanism)

This achieves the same result with tools that actually work today.

## Updating Agent Definitions

After editing any file in `agents/`:
1. Save your changes
2. **Restart your Claude Code session** (agents load at session start only)
3. Verify agent loaded: Try invoking it with `@"agent-name (agent)"`

## References

- [Claude Code Documentation](https://docs.anthropic.com/claude/docs/claude-code)
- [CLAUDE.md](../CLAUDE.md) - Project-specific instructions
- [GitHub: Claude Code Issues](https://github.com/anthropics/claude-code/issues)
