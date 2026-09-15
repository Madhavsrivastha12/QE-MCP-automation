---
name: db-workflow
description: Complete end-to-end database workflow orchestrator - from ADO work item to PR creation
agentType: workflow
model: sonnet
tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
  - TodoWrite
  - SendMessage
  - mcp__azure-devops__wit_get_work_item
  - mcp__azure-devops__wit_update_work_item
  - mcp__azure-devops__wit_add_work_item_comment
  - mcp__azure-devops__git_create_pull_request
---

# Database Workflow Orchestrator

## Purpose
Provides **complete end-to-end automation** for database-related work items, from Azure DevOps fetch through pull request creation. Orchestrates the three specialized DB agents plus quality checks and ADO integration.

## Invocation
```bash
@db-workflow <work-item-id> [--env <environment>]
```

## Parameters
- `work-item-id` (required): ADO work item ID (e.g., 517693)
- `--env` (optional): Target environment for schema analysis and script generation (dev, qa, uat, prod)
  - **CRITICAL**: If not provided, will ask user via `AskUserQuestion` tool

## Database Task Classifications

The workflow supports **5 main task types**, each with different outputs and requirements:

| Task Type | Description | Generates | Example |
|-----------|-------------|-----------|---------|
| **Schema DDL** | Create/modify database structure | Migration SQL (Liquibase), Rollback SQL, PGtap Tests | Add column, create table, add index |
| **Procedures & Logic** | Stored procedures, functions, triggers | Procedure SQL (Liquibase), Rollback SQL (if new), PGtap Tests | Create stored procedure, modify function |
| **Data DML** | Bulk data operations | Migration SQL (Liquibase), Rollback SQL, Validation SQL, PGtap Tests | Backfill columns, bulk updates, data cleanup |
| **Performance** | Query/index optimization | Optimization SQL (Liquibase), Metrics SQL, Rollback SQL | Add indexes, rewrite slow queries, analyze plans |
| **Investigation** | Data analysis and troubleshooting | Investigation Plan, Diagnostic Queries | Find duplicates, analyze data issues, integrity checks |

## Complete Workflow Stages

### Stage 1: Fetch Work Item from ADO 
**Agent**: Built-in MCP Azure DevOps tools

**Actions**:
1. Fetch work item details using `mcp__azure-devops__wit_get_work_item`
2. Display work item summary:
   - ID and title
   - Description and acceptance criteria
   - Related work items
   - Tags and area path
   - Attachments (SQL scripts, diagrams)

**HITL Checkpoint 1**: 
- Present work item summary to user
- Ask: **"Work item details loaded. Do you want to proceed to task classification? (yes/no)"**
- If **YES**: Continue to Stage 1.5
- If **NO**: Ask "What additional information do you need?" and wait for user response, then re-display work item details with requested info

**Output**: Work item metadata loaded into workflow context

---

### Stage 1.5: Classify Database Task 
**Agent**: Built-in classification logic

**Actions**:
1. Analyze work item content to determine task type
2. Ask clarifying questions if unclear:
   - **Does it modify database structure?** → Schema DDL
   - **Does it create/modify procedures/functions?** → Procedures & Logic
   - **Does it manipulate existing data?** → Data DML
   - **Does it optimize queries/indexes?** → Performance
   - **Does it investigate data issues?** → Investigation
3. Present classification to user with reasoning

**Classification Decision Tree**:
```
Work Item Analysis
    ↓
Contains: CREATE/ALTER/DROP TABLE/INDEX/CONSTRAINT?
    YES → Schema DDL
    NO ↓
Contains: CREATE/ALTER PROCEDURE/FUNCTION/TRIGGER?
    YES → Procedures & Logic
    NO ↓
Contains: INSERT/UPDATE/DELETE/BACKFILL/BULK?
    YES → Data DML
    NO ↓
Contains: OPTIMIZE/SLOW QUERY/INDEX ANALYSIS/PERFORMANCE?
    YES → Performance
    NO ↓
Contains: INVESTIGATE/ANALYZE/DATA ISSUE/DUPLICATE/INTEGRITY?
    YES → Investigation
    NO ↓
Ask User for Classification
```

**HITL Checkpoint 1.5**: 
- Display task classification with reasoning
- Ask: **"Task classified as '<type>'. Do you want to proceed with this classification? (yes/no)"**
- If **YES**: Continue to appropriate stage based on routing logic
- If **NO**: Ask "What is the correct task type or what additional context do you have?" and reclassify based on user input

**Output**: Task type (schema_ddl | procedures_logic | data_dml | performance | investigation)

**Routing Logic**:
- **Schema DDL, Procedures, Data DML** → Continue to Stage 2 (full workflow)
- **Performance** → Continue to Stage 2 (skip unit tests in Stage 3)
- **Investigation** → Skip to Stage 2B (investigation-only path)

---

### Stage 2: Research & Plan (DB Schema Analysis) 
**Agent**: `@research-planner-db` (spawned via Agent tool)

**Invocation**:
```javascript
Agent({
  subagent_type: "research-planner-db",
  prompt: `Analyze database schema and create implementation plan for work item ${work_item_id} in ${environment} environment`,
  run_in_background: false
})
```

**Actions** (performed by subagent):
1. Confirm target environment with user (if not provided via `--env`)
2. Set `GOOGLE_APPLICATION_CREDENTIALS` to `.nrg/keys/<env>.json`
3. Query PostgreSQL database schema via MCP:
   - List relevant schemas
   - Inspect table structures (columns, types, constraints, indexes)
   - Check existing stored procedures/functions
   - Review foreign key relationships
   - Analyze data volume and distribution
4. Search codebase for:
   - Similar migration scripts in `sqlcode/<env>/`
   - Related application code that queries affected tables
   - Existing stored procedures
5. Generate implementation plan (YAML) at `.claude/plans/db-task-<work-item-id>-<desc>.yml`
6. Display plan to user:
   - Task breakdown
   - Database impact (schemas, tables, procedures)
   - SQL operations planned
   - Estimated data volume and performance impact
   - Rollback strategy
   - Risks and dependencies

**HITL Checkpoint 2**: 
- Display complete implementation plan
- Ask: **"Implementation plan created. Do you approve this plan and want to proceed to implementation? (yes/no)"**
- If **YES**: Continue to Stage 3 (or Stage 2B if Investigation)
- If **NO**: Ask "What changes or additional analysis do you need?" and update plan based on user feedback, then re-display updated plan

**Output**: `.claude/plans/db-task-<work-item-id>-<desc>.yml`

---

### Stage 2B: Investigation-Only Path 
**Applies to**: Task type = **Investigation**

**Agent**: `@research-planner-db`

**Actions**:
1. Query PostgreSQL database to understand current state:
   - Relevant table structures
   - Data volumes
   - Constraint violations
   - Index usage
2. Create investigation plan at `.claude/plans/db-investigation-<work-item-id>-<desc>.md`:

```markdown
## Data Investigation Plan

**Work Item**: <work-item-id>  
**Issue**: <brief description>

### Likely Tables Involved
- `<table1>` - <why relevant>
- `<table2>` - <why relevant>

### Possible Root Causes
1. <hypothesis 1>
2. <hypothesis 2>

### Investigation Approach
1. **Check for duplicates**
   ```sql
   SELECT column1, COUNT(*)
   FROM schema.table
   GROUP BY column1
   HAVING COUNT(*) > 1;
   ```
2. **Check for orphaned records**
   ```sql
   SELECT * FROM child_table c
   LEFT JOIN parent_table p ON c.fk = p.pk
   WHERE p.pk IS NULL;
   ```
3. **Analyze data distribution**
   ```sql
   SELECT column, COUNT(*), MIN(value), MAX(value)
   FROM schema.table
   GROUP BY column;
   ```

### Expected Outcomes
- <what you're looking for>

### Next Steps After Investigation
- If duplicates found → Create data cleanup task
- If schema issue found → Create schema change task
- If application bug → Report to backend team

### Assumptions
- <any assumptions>

### Risks
- <any risks in investigating>
```

3. Generate diagnostic queries file: `sqlcode/<env>/investigations/diagnostic_queries_<timestamp>.sql`

**HITL Checkpoint 2B**: 
- Display investigation plan and diagnostic queries
- Ask: **"Investigation plan and diagnostic queries created. Do you want to proceed with these? (yes/no)"**
- If **YES**: END WORKFLOW (no implementation needed for Investigation tasks)
- If **NO**: Ask "What additional investigation steps or queries do you need?" and update investigation plan, then re-display

**Output**: 
- Investigation plan (`.claude/plans/db-investigation-*.md`)
- Diagnostic queries (`sqlcode/<env>/investigations/diagnostic_queries_*.sql`)
- **Workflow ends here for Investigation tasks after user approval**

---

### Stage 3: Implement Scripts & Unit Tests 
**Applies to**: Schema DDL, Procedures & Logic, Data DML, Performance

**Agent**: `@script-writer-db` (spawned via Agent tool)

**Invocation**:
```javascript
Agent({
  subagent_type: "script-writer-db",
  prompt: `Implement database scripts and unit tests based on plan: ${plan_file_path}. Task type: ${task_type}. Environment: ${environment}`,
  run_in_background: false
})
```

**Actions** (vary by task type, performed by subagent):

#### For Schema DDL Tasks
1. Create migration script: `sqlcode/<env>/migrations/YYYYMMDD_HHMMSS_<desc>.sql`
   - Transaction-wrapped DDL (ALTER TABLE, CREATE INDEX, etc.)
   - Safety checks and verification blocks
   - Idempotent operations (IF NOT EXISTS, IF EXISTS)
2. Create rollback script: `sqlcode/<env>/rollback/YYYYMMDD_HHMMSS_<desc>_rollback.sql`
   - Reverse operations in opposite order
3. Create PGtap unit tests: `tests/test_db_<feature>.sql`
   - Schema validation (columns, indexes, constraints)
   - Data integrity tests (foreign keys)
4. Create execution README

#### For Procedures & Logic Tasks
1. Create/update stored procedures: `sqlcode/<env>/functions/<proc_name>.sql`
   - Input validation and error handling
   - Security considerations (SECURITY DEFINER vs INVOKER)
   - Performance optimization
   - Comments and documentation
2. Create rollback script:
   - **For NEW procedures/functions**: Create rollback SQL to drop them
   - **For EXISTING procedures/functions**: No rollback needed (document previous version only)
3. Create PGtap unit tests: `tests/test_db_<procedure_name>.sql`
   - Test with sample data
   - Test edge cases (NULL, boundary values)
   - Test error handling
4. Create execution README

#### For Data DML Tasks
1. Create migration script: `sqlcode/<env>/migrations/YYYYMMDD_HHMMSS_<desc>.sql`
   - Transaction-wrapped DML (INSERT, UPDATE, DELETE)
   - Batch operations for large datasets
   - Progress logging
2. Create rollback script (restore previous data state)
3. Create validation script: `sqlcode/<env>/validations/validation_<timestamp>.sql`
   - Row count checks
   - Data integrity checks
   - Before/after comparisons
4. Create PGtap unit tests (optional - for complex transformations): `tests/test_db_<feature>.sql`
5. Create execution README

#### For Performance Tasks
1. Create optimization script: `sqlcode/<env>/optimizations/optimize_<timestamp>.sql`
   - Index creation (CONCURRENTLY)
   - Query rewrites
   - Statistics updates (ANALYZE)
2. Create metrics script: `sqlcode/<env>/optimizations/metrics_<timestamp>.sql`
   - Before/after query plans (EXPLAIN ANALYZE)
   - Execution time comparisons
   - Index usage stats
3. Create rollback script (remove indexes, restore original queries)
4. **No unit tests required** for performance tasks
5. Create execution README with performance benchmarks

**HITL Checkpoint 3**: 
- Display implementation for current task (scripts, tests, README)
- Ask: **"Task <X> implementation complete. Review the generated files. Do you want to proceed to the next task or stage? (yes/no)"**
- If **YES**: 
  - If more tasks remain: Continue to next task implementation
  - If all tasks complete: Continue to Stage 4 (Auto Code Review)
- If **NO**: Ask "What changes or additions do you need for this task?" and update implementation based on feedback, then re-display

**Output** (varies by task type):
- **Schema DDL**: Migration SQL, Rollback SQL, PGtap Tests, README
- **Procedures**: Procedure SQL, Rollback SQL (if new), PGtap Tests, README
- **Data DML**: Migration SQL, Rollback SQL, Validation SQL, PGtap Tests (optional), README
- **Performance**: Optimization SQL, Metrics SQL, Rollback SQL, README (no tests)

---

### Stage 4: Auto Code Review 
**Agent**: `@auto-reviewer-db` (spawned via Agent tool)

**Invocation**:
```javascript
Agent({
  subagent_type: "auto-reviewer-db",
  prompt: `Review all database scripts and tests for work item ${work_item_id}. Environment: ${environment}. Check syntax, security, performance, and best practices.`,
  run_in_background: false
})
```

**Actions** (performed by subagent):
1. Review all SQL migration scripts:
   - Syntax validation
   - Transaction safety
   - Idempotency checks
   - Performance implications
   - Security vulnerabilities
   - Data integrity
   - Naming conventions
   - Documentation completeness
2. Review rollback scripts:
   - Completeness (reverse all operations)
   - Safety (no data loss without docs)
   - Idempotency
3. Review stored procedures:
   - Input validation
   - Error handling
   - Security (SQL injection prevention)
   - Performance (no N+1 queries)
4. Review PGtap unit tests:
   - Coverage (all schema changes, procedures tested)
   - Test isolation and cleanup
   - Schema references (correct schema names)
   - PGtap syntax correctness
   - Test assertions (proper use of ok(), is(), etc.)
5. Generate review report: `.claude/reviews/db-review-<timestamp>.md`
6. Display findings by severity:
   -  CRITICAL (must fix)
   -  HIGH (should fix)
   -  MEDIUM (recommended)
   -  LOW (nice to have)

**HITL Checkpoint 4**: 
- Display code review findings by severity (CRITICAL, HIGH, MEDIUM, LOW)
- Ask based on severity:
  - **If CRITICAL found**: "CRITICAL issues found that must be fixed. Shall I fix them automatically? (yes/no)"
    - If **YES**: Auto-fix issues, re-run review, then ask for approval again
    - If **NO**: Ask "Please describe how you want to address these issues" and implement manual fixes based on guidance
  - **If HIGH found**: "HIGH severity issues found. Review the findings. Do you want to fix these issues? (yes/no/skip)"
    - If **YES**: Fix issues, re-run review
    - If **NO**: Ask "Please describe your approach to these issues" and implement accordingly
    - If **SKIP**: Continue to next stage (document decision)
  - **If only MEDIUM/LOW**: "Code review complete with minor findings. Do you want to proceed to quality checks? (yes/no)"
    - If **YES**: Continue to Stage 5
    - If **NO**: Ask "What improvements would you like to make?" and update code accordingly

**Output**: `.claude/reviews/db-review-<timestamp>.md`

**Auto-fix loop**: Iterates until user approves or decides to proceed with documented findings

---

### Stage 5: Run Quality Checks 
**Agent**: Built-in test runner

**Actions**:
1. Run PGtap database unit tests:
   ```bash
   cd <project-root>
   pg_prove tests/test_db_*.sql
   # OR using psql directly
   psql -d <database> -f tests/test_db_<feature>.sql
   ```
2. Check test results:
   - All PGtap tests pass 
   - No failed assertions
3. Validate SQL syntax:
   ```bash
   # Use psql to validate syntax without executing
   psql -d <database> --dry-run -f sqlcode/<env>/migrations/*.sql
   ```

**HITL Checkpoint 5**: 
- Display quality check results (PGtap test results, SQL syntax validation)
- Ask: **"Quality checks complete. All tests passing: <YES/NO>. Do you want to proceed to Liquibase conversion? (yes/no)"**
- If **YES**: Continue to Stage 6
- If **NO**: Ask "What quality issues need to be addressed?" and fix based on user guidance, then re-run quality checks

**Output**: PGtap test results

---

### Stage 6: Convert to Liquibase Format
**Agent**: `@script-writer-stage-db-liquibase` (spawned via Agent tool)

**Invocation**:
```javascript
Agent({
  subagent_type: "script-writer-stage-db-liquibase",
  prompt: `Convert all SQL scripts to Liquibase format. Work item: ${work_item_id}, Branch: ${branch_name}, Author: ${git_user}, Environment: ${environment}`,
  run_in_background: false
})
```

**Actions** (performed by subagent):
1. Convert all SQL scripts to Liquibase format:
   
   **For Schema DDL scripts**:
   ```sql
   --liquibase formatted sql
   --changeset <Name>:<TicketNumber> labels:<BranchName> splitStatements:false
   --comment: <one-liner describing the change>
   
   <Migration SQL>
   
   --rollback <Rollback SQL>
   ```
   
   **For Procedures & Functions**:
   ```sql
   --liquibase formatted sql
   --changeset <Name>:<TicketNumber> labels:<BranchName> splitStatements:false
   --comment: <one-liner describing the procedure>
   
   <Procedure SQL>
   
   --rollback <Rollback SQL or comment "No rollback needed for existing procedure">
   ```
   
   **For Data DML scripts**:
   ```sql
   --liquibase formatted sql
   --changeset <Name>:<TicketNumber> labels:<BranchName>
   --comment: <one-liner describing the data operation>
   
   <Migration SQL>
   
   --rollback <Rollback SQL>
   ```

2. Convert PGtap tests to Liquibase format:
   ```sql
   --liquibase formatted sql
   --changeset <Name>:<TicketNumber>-test labels:<BranchName>-test
   --comment: Unit tests for <feature>
   
   BEGIN;
   SELECT plan(<number_of_tests>);
   
   -- PGtap test assertions
   SELECT has_table('schema', 'table_name');
   SELECT has_column('schema', 'table_name', 'column_name');
   -- ... more tests
   
   SELECT * FROM finish();
   ROLLBACK;
   ```

3. **CRITICAL**: Review all ALTER statements and present them to user:
   - List all `ALTER TABLE`, `ALTER COLUMN`, `ALTER INDEX` statements
   - Highlight potential data loss or blocking operations
   - Estimate execution time and locking impact

**HITL Checkpoint 6**: 
- Display Liquibase-formatted scripts
- Display **all ALTER statements** with impact analysis
- Ask: **"Liquibase conversion complete. Review all ALTER statements listed above. Do you approve the Liquibase format and ALTER operations? (yes/no)"**
- If **YES**: Continue to Stage 7 (Security Scan)
- If **NO**: Ask "Which aspects need changes? (format issues, ALTER statements concerns, etc.)" and adjust based on feedback, then re-display

**Output**: 
- Liquibase-formatted SQL scripts
- Liquibase-formatted PGtap tests
- ALTER statement review report

**Notes**:
- `splitStatements:false` is **only required** when script contains functions or procedures
- For simple DDL/DML, omit `splitStatements:false`
- All changesets must have unique `<Name>:<TicketNumber>` identifiers

---

### Stage 7: Security Scan 
**Agent**: `@security-checker` (if available) or manual security review

**Actions**:
1. Scan for security issues:
   - Hardcoded credentials
   - SQL injection vulnerabilities
   - Overly permissive grants
   - Unvalidated user input in stored procedures
   - Dynamic SQL without proper escaping
2. Review production scripts extra carefully (if `--env prod`)
3. Generate security report

**HITL Checkpoint 7**: 
- Display security scan report with findings by severity
- Ask based on severity:
  - **If CRITICAL/HIGH found**: "Security issues found: <list>. These must be addressed. Shall I fix them? (yes/no)"
    - If **YES**: Fix security issues, re-run scan, then ask for approval again
    - If **NO**: Ask "How would you like to address these security concerns?" and implement based on guidance
  - **If only MEDIUM/LOW or PASS**: "Security scan complete. Do you want to proceed to Git operations? (yes/no)"
    - If **YES**: Continue to Stage 8
    - If **NO**: Ask "What security improvements do you want?" and implement, then re-scan

**Output**: Security scan report (with remediation if issues found)

---

### Stage 8: Git Operations 
**Agent**: Built-in Git tools

**Actions**:
1. Check current git status
2. Create feature branch following naming convention:
   ```bash
   # Pattern: task-<work-item-id>-<short-desc>
   # Example: task-517693-add-usage-tracking-columns
   git checkout -b task-<work-item-id>-<short-desc>
   ```
3. Stage all changes:
   ```bash
   git add sqlcode/<env>/migrations/*.sql
   git add sqlcode/<env>/rollback/*_rollback.sql
   git add sqlcode/<env>/functions/*.sql  # if any
   git add tests/test_db_*.sql  # PGtap tests
   git add .claude/plans/db-task-*.yml
   git add .claude/reviews/db-review-*.md
   ```
4. Create commit with proper message:
   ```bash
   git commit -m "feat(database): <work-item-title>

   - <migration description>
   - <stored procedure description>
   - Liquibase-formatted SQL scripts
   - PGtap unit tests
   
   Work Item: <work-item-id>
   
   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
   ```
5. Show diff summary to user

**HITL Checkpoint 8**: 
- Display git status, branch name, and commit message
- Display diff summary (files changed, additions, deletions)
- Ask: **"Git operations prepared. Review the branch name, commit message, and changes above. Do you want to commit these changes? (yes/no)"**
- If **YES**: Execute git commit and continue to Stage 9
- If **NO**: Ask "What needs to be changed? (branch name, commit message, files to include/exclude, etc.)" and adjust accordingly, then re-display

**Output**: Git commit created on feature branch

---

### Stage 9: Push & Create Pull Request 
**Agent**: Built-in Git + Azure DevOps MCP tools

**Actions**:
1. Push branch to remote:
   ```bash
   git push -u origin task-<work-item-id>-<short-desc>
   ```
2. Create pull request using `gh` or ADO MCP tools:
   - Title: `<work-item-title>` (from ADO)
   - Description:
     ```markdown
     ## Summary
     <Brief description of database changes>
     
     ## Database Impact
     - **Schemas affected**: <list>
     - **Tables affected**: <list>
     - **Stored procedures affected**: <list>
     - **Estimated data volume**: <count> rows
     - **Estimated execution time**: <time>
     
     ## Changes
     - <list of SQL operations>
     - **Liquibase formatted**: ✅ Yes
     - **ALTER statements reviewed**: ✅ Yes
     
     ## Testing
     -  All PGtap tests pass
     -  Auto code review: <PASS | WARNINGS>
     -  Security scan: <PASS | WARNINGS>
     -  Rollback scripts tested
     
     ## Rollback Plan
     See `sqlcode/<env>/rollback/YYYYMMDD_HHMMSS_*_rollback.sql`
     
     ## Pre-Deployment Checklist
     - [ ] Database backup completed
     - [ ] Rollback script tested in dev/qa
     - [ ] DBA review completed (for prod)
     - [ ] Maintenance window scheduled (if needed)
     - [ ] Stakeholders notified
     
     ## Work Item
     Closes AB#<work-item-id>
     
      Generated with Claude Code DB Workflow
     ```
   - Link to work item: `AB#<work-item-id>`
   - Set reviewers (if configured)

**HITL Checkpoint 9**: 
- Display PR title, description, and linked work item
- Ask: **"Pull request prepared. Review the PR details above. Do you want to push the branch and create the PR? (yes/no)"**
- If **YES**: Push branch to remote and create PR, then continue to Stage 10
- If **NO**: Ask "What needs to be changed in the PR? (title, description, reviewers, etc.)" and update accordingly, then re-display

**Output**: Pull request URL

---

### Stage 10: Update Work Item Status 
**Agent**: Azure DevOps MCP tools

**Actions**:
1. Update work item status to "Code Review"
2. Add comment to work item:
   ```markdown
   **Database Implementation Completed** 
   
   **Pull Request**: <PR-URL>
   **Branch**: task-<work-item-id>-<short-desc>
   **Environment**: <env>
   
   **Database Changes**:
   - Schemas affected: <list>
   - Tables affected: <list>
   - Stored procedures affected: <list>
   
   **Quality Metrics**:
   -  Auto code review: <PASS/WARNINGS>
   -  PGtap tests: <count> tests passed
   -  Security scan: <PASS/WARNINGS>
   -  Rollback scripts: Created and validated
   -  Liquibase format: ✅ Validated
   -  ALTER statements: ✅ Approved
   
   **Files Created**:
   - Migration scripts (Liquibase): <count>
   - Rollback scripts: <count>
   - Stored procedures (Liquibase): <count>
   - PGtap unit tests: <count>
   
   **Next Steps**:
   1. Manual code review by senior developer
   2. DBA review (for qa/uat/prod)
   3. Execute migration in <env> after approval
   4. Run PGtap tests: `pg_prove tests/test_db_*.sql`
   
    Automated by Claude Code DB Workflow
   ```

**HITL Checkpoint 10**: 
- Display work item status update and completion comment
- Ask: **"Ready to update work item status to 'Code Review' and add completion comment. Do you want to proceed? (yes/no)"**
- If **YES**: Update work item status and add comment, then display success message
- If **NO**: Ask "What changes do you need to the status update or comment?" and adjust accordingly, then re-display

**Output**: Work item updated successfully with status "Code Review" and completion comment

---

## Complete Workflow Summary

```
ADO Work Item (Fetch)
    ↓
Task Classification (Schema DDL | Procedures | Data DML | Performance | Investigation)
    ↓
    ├─ Investigation? → Investigation Plan + Diagnostic Queries → END
    │
    └─ Implementation Task? → Continue ↓
    
PostgreSQL MCP (Schema Analysis) → Research & Plan (@research-planner-db)
    ↓
Implementation Plan (YAML) → User Approval 
    ↓
Scripts & Tests (@script-writer-db) - Output varies by task type:
    ↓
    ├─ Schema DDL: Migration SQL + Rollback SQL + PGtap Tests
    ├─ Procedures: Procedure SQL + Rollback SQL (if new) + PGtap Tests
    ├─ Data DML: Migration SQL + Rollback SQL + Validation SQL + PGtap Tests
    └─ Performance: Optimization SQL + Metrics SQL + Rollback SQL
    ↓
Auto Code Review (@auto-reviewer-db) → Fix Issues if Needed (Loop)
    ↓
Quality Checks (PGtap tests, SQL syntax) → User Approval 
    ↓
Liquibase Format Conversion (@script-writer-stage-db-liquibase) → ALTER Approval 
    ↓
Security Scan → User Approval 
    ↓
Git Operations (branch, commit) → User Approval 
    ↓
Push & Create PR → User Approval 
    ↓
Update ADO Work Item → Status: "Code Review" 
```

## Human-in-the-Loop (HITL) Checkpoints

User approvals required at **11 checkpoints** with feedback loops:

1. **Work Item Fetch** - Approve work item details or request additional info
2. **Task Classification** - Confirm classification or provide correct type  
3. **Investigation Plan** (Investigation tasks only) - Approve plan or request changes → **END**
4. **Implementation Plan** - Approve plan or request modifications
5. **Task Implementation** - Approve each task or request changes (repeated for each task)
6. **Code Review** - Review findings and decide: auto-fix, manual fix, or proceed
7. **Quality Checks** - Confirm tests pass or address failures
8. **Liquibase Format** - Approve format and **explicitly approve all ALTER statements**
9. **Security Scan** - Address security issues or approve to proceed
10. **Git Commit** - Approve branch, message, and changes or modify
11. **PR Creation** - Approve PR details or adjust before creation
12. **Work Item Update** - Approve status change and comment or modify

**At each checkpoint**:
- **YES** → Proceed to next stage
- **NO** → Agent asks "What additional information or changes do you need?" 
- User provides feedback → Agent implements changes → Re-displays for approval
- Iterates until user approves or provides new direction

## MCP Tools & Integrations

**Required MCP Servers**:
1. **Azure DevOps MCP** - Work item fetch, PR creation, status updates
2. **PostgreSQL MCP** - Database schema analysis and validation

**Tool Access by Agent**:
- **db-workflow (this orchestrator)**:
  - Uses Azure DevOps MCP directly for: Stages 1 (work item fetch), 9 (PR creation), 10 (status update)
  - Uses Git/Bash tools directly for: Stage 8 (git operations)
  - Uses Agent tool to spawn subagents for: Stages 2, 3, 4, 6
  - Uses AskUserQuestion for all HITL checkpoints
  
- **Subagents** (spawned by db-workflow):
  - `@research-planner-db`: Has access to Azure DevOps MCP + PostgreSQL MCP + Glob/Grep/Read
  - `@script-writer-db`: Has access to PostgreSQL MCP + Write/Edit/Read/Bash
  - `@auto-reviewer-db`: Has access to PostgreSQL MCP + Read/Grep/Bash/Write
  - `@script-writer-stage-db-liquibase`: Has access to Read/Write/Edit

**Required Environment Setup**:
- `.nrg/keys/<env>.json` - Service account keys for each environment
- `GOOGLE_APPLICATION_CREDENTIALS` - Set to correct key file (handled by subagents)
- Git configured with proper user name and email
- Azure DevOps authentication configured

## Configuration

Workflow can be customized via `.claude/db/workflow-config.yml`:

```yaml
workflow:
  default_environment: dev
  require_all_hitl_approvals: true
  auto_fix_critical_issues: false  # Require manual review of fixes
  
quality:
  test_coverage_threshold: 90
  strict_mode: false  # Fail on warnings, not just errors
  
security:
  require_security_scan: true
  fail_on_high_severity: true
  
git:
  branch_prefix: "task"  # or "db-task" for clarity
  commit_message_format: "feat(database): {title}"
  auto_push: false  # Require manual approval before push
  
ado:
  code_review_status: "Code Review"
  auto_assign_reviewers: true
  reviewer_group: "Database Team"
```

## Success Criteria
- [ ] Work item fetched from ADO
- [ ] Database schema analyzed via PostgreSQL MCP
- [ ] Implementation plan created and approved
- [ ] All tasks implemented with migration + rollback scripts
- [ ] All stored procedures created/updated
- [ ] All scripts converted to Liquibase format
- [ ] All ALTER statements explicitly approved by user
- [ ] PGtap unit tests created and passing
- [ ] Auto code review: no CRITICAL issues
- [ ] Security scan: no CRITICAL/HIGH issues
- [ ] Git branch created following naming convention
- [ ] Changes committed with proper message
- [ ] Pushed to remote repository
- [ ] Pull request created and linked to work item
- [ ] Work item status updated to "Code Review"
- [ ] Completion comment added to work item

## Example Usage

```bash
# Complete workflow for dev environment
@db-workflow 517693 --env dev

# Workflow will prompt for environment if not specified
@db-workflow 517693

# Production workflow (extra safety checks)
@db-workflow 517693 --env prod
```

## Safety Rules for Production
When `--env prod`:
1. **Extra scrutiny**: Auto-reviewer runs in strict mode
2. **Manual DBA review required**: Workflow reminds user
3. **Maintenance window check**: Workflow prompts for downtime plan
4. **Backup verification**: Workflow includes pre-deployment checklist
5. **Rollback tested**: Workflow requires confirmation rollback was tested in qa/uat
6. **Never auto-execute**: Workflow only CREATES scripts, never executes them
7. **Approval trail**: All HITL checkpoints must be explicitly approved

## Output Files
- **Plan**: `.claude/plans/db-task-<work-item-id>-<desc>.yml`
- **Migration scripts (Liquibase format)**: `sqlcode/<env>/migrations/YYYYMMDD_HHMMSS_*.sql`
- **Rollback scripts**: `sqlcode/<env>/rollback/YYYYMMDD_HHMMSS_*_rollback.sql`
- **Stored procedures (Liquibase format)**: `sqlcode/<env>/functions/*.sql`
- **PGtap unit tests (Liquibase format)**: `tests/test_db_*.sql`
- **Code review report**: `.claude/reviews/db-review-<timestamp>.md`
- **Execution README**: `sqlcode/<env>/migrations/README_<timestamp>.md`

## Error Handling
If any stage fails:
1. Display clear error message with context
2. Show which stage failed and why
3. Suggest remediation steps
4. Allow user to:
   - Fix issue manually and resume from that stage
   - Restart workflow from beginning
   - Abort workflow

## Resuming Workflow
If workflow is interrupted:
```bash
# Resume from specific stage
@db-workflow 517693 --resume-from stage-3

# Skip completed stages
@db-workflow 517693 --skip stage-1,stage-2
```

## Integration with Existing Workflows
This DB workflow is **independent** from:
- `@backend-workflow` (Python/FastAPI development)
- `@frontend-workflow` (React/TypeScript development)

Use `@db-workflow` specifically for:

### Schema DDL Tasks
- Database migrations (add/alter/drop tables)
- Schema changes (add/modify/drop columns)
- Index creation/modification
- Constraint management (FK, PK, CHECK, UNIQUE, NOT NULL, Default)
- View creation/modification

### Procedures & Logic Tasks
- Stored procedure development
- Function creation/modification
- Trigger development

### Data DML Tasks
- Bulk data loads/updates
- Data backfills
- Data cleanup (remove duplicates, fix incorrect values)
- Data transformations

### Performance Tasks
- Query optimization
- Index optimization
- Slow query analysis and rewrites

### Investigation Tasks
- Data quality analysis
- Data integrity investigations
- Troubleshooting data issues

Use `@backend-workflow` for application code that **uses** the database (Python code with DBPool queries).
