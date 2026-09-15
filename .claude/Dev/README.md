# Usage Empire - Development Agents

Complete suite of specialized agents for implementing Azure DevOps work items with full automation from planning through PR creation.

## 🚀 Quick Start

### Full Automated Workflow

```bash
# Backend work item (Python/FastAPI)
@backend-workflow 517693

# Frontend work item (React/TypeScript)
@frontend-workflow 517693
```

These orchestrator agents handle everything end-to-end with 6 HITL (Human-in-the-Loop) checkpoints.

### Individual Agent Usage

You can also run each agent independently:

```bash
# 1. Research & Planning
@research-planner 517693 --service ue-api

# 2. Implementation (choose backend or frontend)
@implementation-agent-backend .claude/plans/task-517693.yml
@implementation-agent-frontend .claude/plans/task-517693.yml

# 3. Quality Checks (choose backend or frontend)
@run-checker-backend ue-api
@run-checker-frontend

# 4. Code Review
@code-reviewer --auto-fix

# 5. Security Scan
@security-checker --severity high
```

## 📁 Agent Structure

```
.claude/Dev/
├── shared/                    # Agents that work for both backend & frontend
│   ├── research-planner.md    # ADO fetch + codebase analysis + plan creation
│   ├── code-reviewer.md       # Code quality review (Python & TypeScript)
│   └── security-checker.md    # Security vulnerability scanning
│
├── backend/                   # Python/FastAPI specific agents
│   ├── backend-workflow.md    # Main orchestrator for backend work items
│   ├── implementation-agent-backend.md
│   └── run-checker-backend.md
│
└── frontend/                  # React/TypeScript specific agents
    ├── frontend-workflow.md   # Main orchestrator for frontend work items
    ├── implementation-agent-frontend.md
    └── run-checker-frontend.md
```

## 🤖 Agent Catalog

### Orchestrator Agents

#### `@backend-workflow`
**Purpose**: End-to-end automation for backend (Python/FastAPI) work items  
**Services**: ue-api, calcmanager, lfp-api, orch, batch-load-job  
**What it does**:
- Fetches work item from ADO
- Creates implementation plan
- Implements all tasks with tests
- Runs quality checks (tests, lint, coverage ≥80%)
- Runs code review
- Runs security scan
- Creates git branch
- Commits changes
- Pushes to remote
- Creates PR linked to work item
- Updates work item status to "Code Review"

**Usage**:
```bash
@backend-workflow <work-item-id>

# Example
@backend-workflow 517693
```

**HITL Checkpoints**: 6
1. Work item fetch approval
2. Plan approval
3. Each task completion approval
4. Security scan approval
5. Git push approval
6. PR creation approval

---

#### `@frontend-workflow`
**Purpose**: End-to-end automation for frontend (React/TypeScript) work items  
**Service**: ue-frontend  
**What it does**: Same as backend-workflow but for React/TypeScript code

**Usage**:
```bash
@frontend-workflow <work-item-id>

# Example
@frontend-workflow 517693
```

**HITL Checkpoints**: 6 (same as backend-workflow)

---

### Shared Agents

#### `@research-planner`
**Purpose**: Fetch ADO work item, analyze codebase, create implementation plan  
**Works for**: Both backend and frontend  
**Output**: YAML plan file at `.claude/plans/task-<id>-<desc>.yml`

**Usage**:
```bash
# Auto-detect service from work item
@research-planner <work-item-id>

# Explicit service specification
@research-planner <work-item-id> --service ue-api
@research-planner <work-item-id> --service ue-frontend
```

**What it analyzes**:
- Work item title, description, acceptance criteria
- Related work items, attachments
- Existing codebase patterns
- Similar implementations
- Required files to modify/create

**Output format**:
```yaml
work_item_id: 517693
title: "Add forecast endpoint"
service: "ue-api"
tasks:
  - id: 1
    title: "Implement endpoint"
    files_to_modify: [...]
    tests_required: [...]
```

---

#### `@code-reviewer`
**Purpose**: Review current git diff for quality, best practices, potential issues  
**Works for**: Both Python and TypeScript/React code

**Usage**:
```bash
# Standard review (medium+ severity)
@code-reviewer

# Auto-fix applicable issues
@code-reviewer --auto-fix

# Only critical and high severity
@code-reviewer --severity high
```

**What it checks**:
- **Correctness**: Logic errors, edge cases
- **Best Practices**: Language-specific patterns
- **Code Quality**: DRY, complexity, documentation
- **Performance**: N+1 queries, inefficient loops
- **Security**: Injection, XSS, secrets exposure

**Auto-fixes**:
- Missing type hints
- Hardcoded schema names → `app_env.connection_details.db_schema`
- SQL string interpolation → parameterized queries
- Formatting issues

---

#### `@security-checker`
**Purpose**: Scan for security vulnerabilities and OWASP top 10 issues  
**Works for**: Both backend and frontend

**Usage**:
```bash
# Standard scan (high + critical only)
@security-checker

# Include all severities
@security-checker --severity low

# Include dependency CVE scan
@security-checker --include-dependencies
```

**What it scans**:
- **Secrets**: API keys, passwords, service account keys
- **OWASP Top 10**: SQL injection, XSS, broken auth, etc.
- **Python-specific**: eval/exec, pickle, path traversal
- **React-specific**: dangerouslySetInnerHTML, localStorage secrets
- **Dependencies**: Known CVEs (optional)

**Severity levels**:
- **CRITICAL**: Exposed secrets, SQL injection, RCE → Do not merge
- **HIGH**: XSS, broken auth → Fix before merge
- **MEDIUM**: Weak crypto, missing validation → Fix in sprint
- **LOW**: Missing headers → Nice to have

---

### Backend-Specific Agents

#### `@implementation-agent-backend`
**Purpose**: Implement tasks from plan for Python/FastAPI services  
**Services**: ue-api, calcmanager, lfp-api, orch, batch-load-job

**Usage**:
```bash
# Implement all tasks
@implementation-agent-backend .claude/plans/task-517693.yml

# Implement specific task only
@implementation-agent-backend .claude/plans/task-517693.yml --task 3
```

**Patterns followed**:
- ✅ DBPool for database access
- ✅ `app_env.connection_details.db_schema` (no hardcoded schemas)
- ✅ Parameterized SQL queries (`$1, $2, ...`)
- ✅ Type hints on all functions
- ✅ Domain exception hierarchy
- ✅ Async patterns with asyncpg
- ✅ In-memory cache usage

**Test requirements**:
- Happy path + edge cases + error cases
- Mock DBPool with conftest pattern
- Coverage ≥90%

---

#### `@run-checker-backend`
**Purpose**: Execute all quality checks for Python services  
**Services**: ue-api, calcmanager, lfp-api, orch, batch-load-job

**Usage**:
```bash
# Auto-detect service from current directory
@run-checker-backend

# Explicit service
@run-checker-backend ue-api

# Skip specific checks
@run-checker-backend --skip-tests
@run-checker-backend --skip-lint
```

**Checks performed** (in order):
1. ✅ **Format Check**: `black --check --line-length 120`
2. ✅ **Lint Check**: `flake8 --max-line-length 180`
3. ✅ **Type Check**: `mypy src/` (if configured)
4. ✅ **Import Check**: Verify all modules importable
5. ✅ **Unit Tests**: `uv run pytest tests/ --cov=src`
6. ✅ **Coverage**: ≥90% threshold
7. ✅ **Test Files**: Verify all source files have tests

**Exit codes**:
- `0`: All checks passed
- `1`: Format/lint failures
- `2`: Test failures
- `3`: Coverage below threshold

---

### Frontend-Specific Agents

#### `@implementation-agent-frontend`
**Purpose**: Implement tasks from plan for React/TypeScript frontend  
**Service**: ue-frontend

**Usage**:
```bash
# Implement all tasks
@implementation-agent-frontend .claude/plans/task-517693.yml

# Implement specific task only
@implementation-agent-frontend .claude/plans/task-517693.yml --task 2
```

**Patterns followed**:
- ✅ No `any` types (use proper types or `unknown`)
- ✅ Zod schemas at all API boundaries
- ✅ TanStack Query for data fetching
- ✅ Proper hook dependency arrays
- ✅ Accessibility (a11y) attributes
- ✅ TypeScript strict mode
- ✅ Memoization (useMemo, useCallback)

**Test requirements**:
- Component rendering + interactions + errors
- Mock API calls
- Accessibility checks
- Coverage ≥70%

---

#### `@run-checker-frontend`
**Purpose**: Execute all quality checks for React/TypeScript frontend  
**Service**: ue-frontend

**Usage**:
```bash
# Run all checks
@run-checker-frontend

# Skip specific checks
@run-checker-frontend --skip-tests
@run-checker-frontend --skip-types

# Auto-fix lint and format
@run-checker-frontend --auto-fix
```

**Checks performed** (in order):
1. ✅ **Type Check**: `tsc --noEmit` (strict mode)
2. ✅ **Lint Check**: `eslint`
3. ✅ **Format Check**: `prettier --check`
4. ✅ **Import Check**: `npm run build:dev` (Vite)
5. ✅ **Unit Tests**: `npm test -- --coverage`
6. ✅ **Coverage**: ≥70% threshold
7. ✅ **Test Files**: Verify components/hooks have tests
8. ✅ **Routes**: Route tree up-to-date

**Exit codes**:
- `0`: All checks passed
- `1`: Format/lint failures
- `2`: Type errors
- `3`: Test failures
- `4`: Coverage below threshold

---

## 🎯 Workflow Comparison

### Backend Workflow
| Check | Tool | Threshold |
|-------|------|-----------|
| Format | black (line-length 120) | Required |
| Lint | flake8 (max 180, ignore E203,W503) | Required |
| Type | mypy (optional) | If configured |
| Tests | pytest | All pass |
| Coverage | pytest-cov | ≥80% |
| Language | Python 3.13 | - |
| Package Manager | uv | - |

### Frontend Workflow
| Check | Tool | Threshold |
|-------|------|-----------|
| Format | prettier | Required |
| Lint | eslint | Required |
| Type | tsc --noEmit | Required |
| Tests | jest | All pass |
| Coverage | jest --coverage | ≥70% |
| Language | TypeScript 5 | - |
| Package Manager | npm | - |

---

## 📊 Definition of Done

### Using Workflow Agents (Automated)
- [ ] All 6 HITL checkpoints approved
- [ ] Plan approved by developer
- [ ] All plan tasks implemented with unit tests
- [ ] run-checker: all checks PASS (coverage ≥80% backend / ≥70% frontend)
- [ ] code-reviewer: no remaining findings
- [ ] security-checker: no CRITICAL or HIGH findings
- [ ] Git branch created following naming convention
- [ ] Changes committed with proper message format
- [ ] Pushed to remote repository
- [ ] Pull request created and linked to work item
- [ ] Work item status updated to "Code Review"
- [ ] Completion comment added to work item
- [ ] No TODO / FIXME left in new code

### Manual Workflow (Individual Agents)
- [ ] Plan approved by developer (YES typed in terminal)
- [ ] All plan tasks implemented
- [ ] Unit tests written and passing for every task
- [ ] run-checker: all checks PASS
- [ ] code-reviewer: no remaining findings
- [ ] security-checker: no CRITICAL or HIGH findings
- [ ] No TODO / FIXME left in new code
- [ ] Manual git operations (branch, commit, push, PR)
- [ ] Manual work item status update

---

## 🔧 MCP Tools Used

The agents use Azure DevOps MCP tools for:
- **Work Items**: Fetch, update, comment
- **Repositories**: Branch, commit, push
- **Pull Requests**: Create, link to work items

Standard Claude Code tools:
- **Read, Write, Edit**: File operations
- **Bash**: Command execution
- **Glob, Grep**: Code search

---

## 📚 Additional Resources

- [CLAUDE.md](../../CLAUDE.md) - Project-wide development guidelines
- [AGENTS.md](../../AGENTS.md) - Environment awareness and MCP configuration
- [QUICK_START.md](../QUICK_START.md) - Quick start guide for workflow agents
- [ORCHESTRATOR_FLOW.md](../ORCHESTRATOR_FLOW.md) - Detailed workflow documentation

---

## ⚠️ Important Notes

1. **Agent Session Restart**: After editing any agent files in `.claude/Dev/`, you MUST restart the Claude Code session for changes to take effect.

2. **Environment Selection**: Always confirm target environment (dev/qa/uat/prod) before using MCP tools. See [AGENTS.md](../../AGENTS.md).

3. **Coverage Thresholds**:
   - Backend: ≥80% (enforced by pre-commit hook at 90%)
   - Frontend: ≥70% (enforced by husky pre-commit hook at 90%)

4. **Pre-commit Hooks**:
   - Backend: `.git/hooks/pre-commit` (coverage ≥90%, branch naming)
   - Frontend: Husky hooks (coverage ≥90%, lint, type-check)

5. **Branch Naming**: Must follow `task-<ticket>-<desc>` or `bug-<ticket>-<desc>` pattern (enforced by pre-commit hook)

6. **Commit Format**: 
   - `feat(<area>): <subject>` for features
   - `fix(<area>): <subject>` for bugs
   - `Merged PR <number>: <description>` for PR merges

---

## 🆘 Troubleshooting

### Agent not found
- Restart Claude Code session after creating/editing agents
- Verify agent file has proper frontmatter with `name:` field

### Tests failing in run-checker
- Ensure you're in the correct directory
- For backend: Use `uv run pytest` (not bare `pytest`)
- For frontend: Check jest.setup.ts for proper mocks (ResizeObserver, etc.)

### Coverage below threshold
- Check `.coveragerc` (backend) or `jest.config.js` (frontend) for excluded files
- Use `--cov-report=term-missing` to see uncovered lines
- Write tests for uncovered code paths

### MCP tools not working
- Verify `.mcp.json` configuration
- Check `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- Refer to [AGENTS.md](../../AGENTS.md) for environment-specific setup

---

## 🎓 Learning Path

**For new developers:**

1. Start with individual agents to understand each step:
   ```bash
   @research-planner 517693
   @implementation-agent-backend .claude/plans/task-517693.yml --task 1
   @run-checker-backend
   @code-reviewer
   @security-checker
   ```

2. Once comfortable, use the full orchestrator:
   ```bash
   @backend-workflow 517693
   ```

3. Review the generated plan files in `.claude/plans/` to understand the planning logic

4. Read agent source files in `.claude/Dev/` to see how they work

**For experienced developers:**

- Jump straight to `@backend-workflow` or `@frontend-workflow`
- Use individual agents for debugging or re-running specific steps
- Customize agent files for team-specific patterns

---

## 📝 Version History

- **v1.0** (2026-07-14): Initial agent suite creation
  - 3 shared agents (research-planner, code-reviewer, security-checker)
  - 4 specialized agents (2 backend, 2 frontend)
  - 2 orchestrator agents (backend-workflow, frontend-workflow)
