# Database AI Flow Agents

This folder contains specialized agents for database-related work items, providing complete automation from Azure DevOps work item fetch through pull request creation.

## 🎯 Overview

The DB AI Flow orchestrates three specialized agents plus quality checks to handle **5 types of database tasks**:

1. **Schema DDL** - Create/modify database structure (tables, columns, indexes, constraints)
2. **Procedures & Logic** - Stored procedures, functions, triggers
3. **Data DML** - Bulk data operations (backfills, updates, cleanup)
4. **Performance** - Query/index optimization
5. **Investigation** - Data analysis and troubleshooting

Each task type has different outputs and workflow paths.

## 📁 Folder Structure

```
.claude/db/
├── README.md                           # This file - complete documentation
├── db-workflow.md                      # Workflow orchestrator agent
└── agents/                             # Individual specialized agents
    ├── research-planner-db.md          # Research & plan agent
    ├── script-writer-db.md             # Script & test writer agent
    ├── script-writer-stage-db-liquibase.md  # Liquibase format converter
    └── auto-reviewer-db.md             # Auto code review agent
```

## 📝 Agent Files

| Agent | File | Purpose |
|-------|------|---------|
| **DB Workflow Orchestrator** | [db-workflow.md](db-workflow.md) | Complete end-to-end automation - orchestrates all DB agents |
| **Research & Plan (DB)** | [agents/research-planner-db.md](agents/research-planner-db.md) | Fetches ADO work item, analyzes PostgreSQL schema via MCP, creates implementation plan |
| **Script Writer (DB)** | [agents/script-writer-db.md](agents/script-writer-db.md) | Implements migration scripts, rollback scripts, stored procedures, and PGtap unit tests |
| **Liquibase Converter** | [agents/script-writer-stage-db-liquibase.md](agents/script-writer-stage-db-liquibase.md) | Converts all SQL scripts to Liquibase format with changeset metadata and validates ALTER statements |
| **Auto Reviewer (DB)** | [agents/auto-reviewer-db.md](agents/auto-reviewer-db.md) | Automated code review for SQL scripts, procedures, and tests |

## 🚀 Quick Start

### For Complete Automation (Recommended)

```bash
# Run complete DB workflow (will prompt for environment)
@db-workflow 517693

# Specify environment explicitly
@db-workflow 517693 --env dev
```

This single command runs the entire flow:
1. Fetches work item from ADO
2. Analyzes database schema via PostgreSQL MCP
3. Creates implementation plan
4. Implements scripts and PGtap tests
5. Runs auto code review
6. Runs quality checks (PGtap tests, SQL syntax)
7. Converts to Liquibase format and validates ALTER statements
8. Runs security scan
9. Creates git branch and commit
10. Pushes and creates pull request
11. Updates ADO work item status

### For Individual Stages (Manual)

```bash
# Step 1: Research and plan
@research-planner-db 517693 --env dev

# Step 2: Implement scripts and tests
@script-writer-db .claude/plans/db-task-517693-add-columns.yml

# Step 3: Auto review
@auto-reviewer-db

# Step 4: Manual quality checks
cd <project-root>
pg_prove tests/test_db_*.sql
```

## 🔄 Complete Workflow Flow

```
ADO Work Item (Fetch)
    ↓
Task Classification (Schema DDL | Procedures | Data DML | Performance | Investigation)
    ↓
    ├─ Investigation? → Investigation Plan + Diagnostic Queries → END
    │
    └─ Implementation Task? → Continue ↓
    
PostgreSQL MCP (Schema Analysis) → Research & Plan
    ↓
Implementation Plan (YAML) → User Approval ✅
    ↓
Scripts & Tests - Output varies by task type:
    ↓
    ├─ Schema DDL: Migration SQL + Rollback SQL + PGtap Tests
    ├─ Procedures: Procedure SQL + Rollback SQL (if new) + PGtap Tests
    ├─ Data DML: Migration SQL + Rollback SQL + Validation SQL + PGtap Tests
    └─ Performance: Optimization SQL + Metrics SQL + Rollback SQL (no unit tests)
    ↓
Auto Code Review → Fix Issues if Needed (Loop)
    ↓
Quality Checks (PGtap tests, SQL syntax) → User Approval ✅
    ↓
Liquibase Format Conversion → ALTER Approval ✅
    ↓
Security Scan → User Approval ✅
    ↓
Git Operations (branch, commit) → User Approval ✅
    ↓
Push & Create PR → User Approval ✅
    ↓
Update ADO Work Item → Status: "Code Review" ✅
```

## ✅ Human-in-the-Loop (HITL) Checkpoints

The workflow requires user approval at checkpoints (varies by task type):

### For Implementation Tasks (Schema DDL, Procedures, Data DML, Performance)
**9 checkpoints**:
1. ✅ Work item details correct
2. ✅ Task classification confirmed
3. ✅ Implementation plan approved
4. ✅ Each task implementation approved (iterative)
5. ✅ Code review findings addressed
6. ✅ Quality checks passed (PGtap tests)
7. ✅ Liquibase format validated and ALTER statements approved
8. ✅ Security scan passed
9. ✅ Git commit approved
10. ✅ PR creation approved

### For Investigation Tasks
**2 checkpoints only**:
1. ✅ Work item details correct
2. ✅ Task classification confirmed as "Investigation"

Then workflow generates investigation plan + diagnostic queries and **ENDS** (no PR created)

## 🔧 Environment Setup

### Required MCP Servers

1. **Azure DevOps MCP** - Work item management and PR creation
2. **PostgreSQL MCP** - Database schema analysis and validation

### Required Files

```
.nrg/keys/
├── dev.json      # Dev environment service account
├── qa.json       # QA environment service account
├── uat.json      # UAT environment service account
└── prod.json     # Production service account
```

### Environment Variable

Before running database queries, ensure `GOOGLE_APPLICATION_CREDENTIALS` points to the correct key:

```bash
# For dev environment
export GOOGLE_APPLICATION_CREDENTIALS=".nrg/keys/dev.json"

# For production (read-only analysis)
export GOOGLE_APPLICATION_CREDENTIALS=".nrg/keys/prod.json"
```

**Note**: The workflow agents handle this automatically if `--env` is specified.

## 📝 Output Files (varies by task type)

### For Schema DDL Tasks
- `.claude/plans/db-task-<work-item-id>-<desc>.yml` - Implementation plan
- `sqlcode/<env>/migrations/YYYYMMDD_HHMMSS_<desc>.sql` - Migration scripts (Liquibase format)
- `sqlcode/<env>/rollback/YYYYMMDD_HHMMSS_<desc>_rollback.sql` - Rollback scripts
- `tests/test_db_<feature>.sql` - PGtap unit tests (Liquibase format)
- `sqlcode/<env>/migrations/README_<timestamp>.md` - Execution instructions
- `.claude/reviews/db-review-<timestamp>.md` - Auto code review report
- `.claude/reviews/liquibase-conversion-<timestamp>.md` - Liquibase conversion report

### For Procedures & Logic Tasks
- `.claude/plans/db-task-<work-item-id>-<desc>.yml` - Implementation plan
- `sqlcode/<env>/functions/<proc_name>.sql` - Stored procedures (Liquibase format)
- `sqlcode/<env>/rollback/<proc_name>_rollback.sql` - Previous version backup (if new)
- `tests/test_db_<procedure_name>.sql` - PGtap unit tests (Liquibase format)
- `sqlcode/<env>/functions/README_<timestamp>.md` - Documentation
- `.claude/reviews/db-review-<timestamp>.md` - Auto code review report
- `.claude/reviews/liquibase-conversion-<timestamp>.md` - Liquibase conversion report

### For Data DML Tasks
- `.claude/plans/db-task-<work-item-id>-<desc>.yml` - Implementation plan
- `sqlcode/<env>/migrations/YYYYMMDD_HHMMSS_<desc>.sql` - Data migration scripts (Liquibase format)
- `sqlcode/<env>/rollback/YYYYMMDD_HHMMSS_<desc>_rollback.sql` - Rollback scripts
- `sqlcode/<env>/validations/validation_<timestamp>.sql` - Before/after validation
- `sqlcode/<env>/migrations/README_<timestamp>.md` - Execution instructions
- `.claude/reviews/db-review-<timestamp>.md` - Auto code review report
- `.claude/reviews/liquibase-conversion-<timestamp>.md` - Liquibase conversion report
- `tests/test_db_<feature>.sql` - PGtap unit tests (optional, for complex transformations)

### For Performance Tasks
- `.claude/plans/db-task-<work-item-id>-<desc>.yml` - Implementation plan
- `sqlcode/<env>/optimizations/optimize_<timestamp>.sql` - Optimization scripts (Liquibase format)
- `sqlcode/<env>/optimizations/metrics_<timestamp>.sql` - Performance metrics
- `sqlcode/<env>/rollback/optimize_<timestamp>_rollback.sql` - Rollback scripts
- `sqlcode/<env>/optimizations/README_<timestamp>.md` - Benchmarks and documentation
- `.claude/reviews/db-review-<timestamp>.md` - Auto code review report
- `.claude/reviews/liquibase-conversion-<timestamp>.md` - Liquibase conversion report
- **No unit tests** (validation via metrics comparison)

### For Investigation Tasks
- `.claude/plans/db-investigation-<work-item-id>-<desc>.md` - Investigation plan
- `sqlcode/<env>/investigations/diagnostic_queries_<work-item-id>_<timestamp>.sql` - Diagnostic queries
- **Workflow ENDS here** - no implementation, no PR

## 🎯 Use Cases

### When to Use DB Workflow

Use `@db-workflow` for:
- ✅ Database schema migrations (ALTER TABLE, ADD COLUMN, etc.)
- ✅ Creating/modifying stored procedures or functions
- ✅ Adding/removing indexes or constraints
- ✅ Data model changes
- ✅ Database query optimization tasks
- ✅ Creating new database tables
- ✅ Database refactoring

### When NOT to Use DB Workflow

**Do NOT use** `@db-workflow` for:
- ❌ Application code changes (use `@backend-workflow`)
- ❌ Frontend changes (use `@frontend-workflow`)
- ❌ API endpoint development (use `@backend-workflow`)
- ❌ Bug fixes in application logic (use appropriate workflow)

The DB workflow is **independent** from backend and frontend workflows. Use it specifically for database-layer work.

## 🔒 Safety Features

### For All Environments
- Transaction-wrapped migrations (BEGIN/COMMIT)
- Idempotent scripts (IF NOT EXISTS / IF EXISTS)
- Automatic rollback script generation
- Verification blocks in every migration
- SQL injection prevention checks
- Security vulnerability scanning
- Performance impact analysis

### Extra Safety for Production (`--env prod`)
- ⚠️ Strict mode auto-review
- ⚠️ Manual DBA review required
- ⚠️ Maintenance window check
- ⚠️ Backup verification checklist
- ⚠️ Rollback must be tested in qa/uat first
- ⚠️ Never auto-executes - only creates scripts
- ⚠️ All HITL checkpoints must be explicitly approved

## 🧪 Quality Standards

### Test Coverage
- **PGtap tests required for**: Every schema change, every stored procedure, every constraint
- **Test quality**: Comprehensive assertions, edge cases covered, proper test isolation

### Code Quality
- **SQL**: Transaction safety, idempotency, verification blocks, comments
- **Liquibase format**: Valid changeset metadata, proper rollback annotations, unique IDs
- **PGtap tests**: Correct syntax, proper use of assertions (has_table, has_column, etc.)

### Review Severity Levels
- **❌ CRITICAL**: Must fix before merge (SQL injection, hardcoded credentials, missing rollback)
- **⚠️ HIGH**: Should fix before merge (missing verification, poor error handling)
- **ℹ️ MEDIUM**: Recommended (missing comments, suboptimal indexes)
- **✅ LOW**: Nice to have (naming improvements, refactoring opportunities)

## 📊 Agent Responsibilities

### @research-planner-db
- Fetches work item from ADO
- Queries PostgreSQL schema via MCP
- Analyzes table structures, constraints, indexes
- Reviews existing SQL scripts for patterns
- Creates detailed implementation plan (YAML)
- Estimates performance impact and data volume

### @script-writer-db
- Implements migration scripts with safety checks
- Creates corresponding rollback scripts
- Writes/updates stored procedures
- Generates comprehensive PGtap unit tests
- Creates execution documentation (README)
- Follows project SQL conventions

### @script-writer-stage-db-liquibase
- Converts all SQL scripts to Liquibase format
- Adds changeset metadata (author, ticket, labels)
- Adds rollback annotations to migration scripts
- Handles `splitStatements:false` for procedures/functions
- Extracts and validates ALL ALTER statements
- Categorizes ALTER statements by risk (Low/Medium/High)
- Requires explicit user approval for ALTER operations
- Generates Liquibase conversion report

### @auto-reviewer-db
- Reviews SQL syntax and semantics
- Validates transaction safety and idempotency
- Checks for security vulnerabilities (SQL injection)
- Analyzes performance implications
- Reviews rollback script completeness
- Validates PGtap test coverage and quality
- Generates detailed review report with severity levels

### @db-workflow
- Orchestrates all four specialized agents
- Manages environment setup (credentials, keys)
- Runs quality checks (PGtap tests, SQL syntax)
- Converts scripts to Liquibase format
- Performs security scanning
- Handles git operations (branch, commit, push)
- Creates pull request with detailed description
- Updates ADO work item status and adds completion comment

## 🔄 Workflow Resumption

If the workflow is interrupted, you can resume from a specific stage:

```bash
# Resume from implementation stage
@db-workflow 517693 --resume-from stage-3

# Skip completed stages
@db-workflow 517693 --skip stage-1,stage-2
```

## 🛠️ Configuration

Customize workflow behavior via `.claude/db/workflow-config.yml`:

```yaml
workflow:
  default_environment: dev
  require_all_hitl_approvals: true
  auto_fix_critical_issues: false
  
quality:
  test_coverage_threshold: 90
  strict_mode: false
  
security:
  require_security_scan: true
  fail_on_high_severity: true
  
git:
  branch_prefix: "task"
  commit_message_format: "feat(database): {title}"
  auto_push: false
  
ado:
  code_review_status: "Code Review"
  auto_assign_reviewers: true
  reviewer_group: "Database Team"
```

## 📚 Additional Resources

- **PostgreSQL MCP Documentation**: [Link to MCP docs]
- **Azure DevOps MCP Documentation**: [Link to ADO MCP docs]
- **Project CLAUDE.md**: [../../CLAUDE.md](../../CLAUDE.md) - Overall project guidelines
- **Project AGENTS.md**: [../../AGENTS.md](../../AGENTS.md) - Environment and credential setup

## 🤝 Integration with Other Workflows

| Workflow | Folder | Purpose | Integration Point |
|----------|--------|---------|-------------------|
| **Backend Workflow** | `.claude/Dev/backend/` | Python/FastAPI development | Backend uses DB schema via DBPool |
| **Frontend Workflow** | `.claude/Dev/frontend/` | React/TypeScript UI | Frontend displays data from backend APIs |
| **BA Workflow** | `.claude/BA/` | Business Analyst tools | BA defines requirements for DB changes |
| **DB Workflow** | `.claude/db/` (this folder) | Database layer development | **Independent** - creates DB foundation |

**Typical flow**:
1. BA creates work item with database requirements
2. **DB Workflow** implements schema changes, migrations, procedures
3. Backend Workflow uses new schema via DBPool in application code
4. Frontend Workflow displays data via backend APIs

## ⚠️ Important Notes

1. **Agent Loading**: After creating or modifying agent files in `.claude/db/`, you **MUST restart Claude Code** for changes to take effect (agents load only at session start)

2. **Environment Confirmation**: Always confirm which environment (dev/qa/uat/prod) before running database queries

3. **Credentials**: Ensure `.nrg/keys/` directory has read permissions before workflow runs

4. **Never Execute Production DDL**: Workflows only **CREATE script files** - never auto-execute them. Manual DBA review required for production.

5. **Rollback Testing**: Always test rollback scripts in dev/qa before promoting to higher environments

## 📞 Getting Help

- **For workflow issues**: Check [db-workflow.md](db-workflow.md) troubleshooting section
- **For MCP connection issues**: See [../../AGENTS.md](../../AGENTS.md)
- **For general project guidance**: See [../../CLAUDE.md](../../CLAUDE.md)

## 🎉 Success Criteria

A DB workflow is complete when:
- ✅ Work item fetched from ADO
- ✅ Database schema analyzed via PostgreSQL MCP
- ✅ Implementation plan approved by user
- ✅ All migration + rollback scripts created
- ✅ All stored procedures implemented
- ✅ All scripts converted to Liquibase format
- ✅ All ALTER statements explicitly approved by user
- ✅ PGtap unit tests created and passing
- ✅ Auto review: no CRITICAL issues
- ✅ Security scan: no CRITICAL/HIGH issues
- ✅ Git branch created (correct naming)
- ✅ Changes committed (proper message format)
- ✅ Pushed to remote
- ✅ Pull request created and linked to work item
- ✅ Work item status updated to "Code Review"
- ✅ Completion comment added to work item

---

**Generated**: 2026-07-19  
**Version**: 1.0  
**Maintained by**: Usage Empire Development Team
