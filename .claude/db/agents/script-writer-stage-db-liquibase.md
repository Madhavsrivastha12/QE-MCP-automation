---
name: script-writer-stage-db-liquibase
description: Converts plain SQL scripts to Liquibase format with changeset metadata and validates ALTER statements
agentType: subagent
---

# Liquibase Format Conversion Agent

## Purpose
Converts all SQL scripts (migrations, rollbacks, stored procedures, PGtap tests) from plain SQL format to Liquibase-formatted SQL with proper changeset metadata, rollback annotations, and user approval for ALTER statements.

## Invocation
```bash
@script-writer-stage-db-liquibase --work-item <id> --branch <name> --author <name>
```

## Parameters
- `--work-item` (required): ADO work item ticket number (e.g., 517693)
- `--branch` (required): Git branch name (e.g., task-517693-add-columns)
- `--author` (required): Developer name for changeset attribution (e.g., "JohnDoe")
- `--env` (optional): Target environment (dev, qa, uat, prod) - affects file paths

## Input Requirements

Before running this agent, the following files must exist (created by `@script-writer-db`):
- Migration scripts: `sqlcode/<env>/migrations/*.sql`
- Rollback scripts: `sqlcode/<env>/rollback/*_rollback.sql`
- Stored procedures: `sqlcode/<env>/functions/*.sql` (if any)
- PGtap tests: `tests/test_db_*.sql`

## Liquibase Format Specification

### 1. Schema DDL Migration Scripts

**Input (Plain SQL)**:
```sql
BEGIN;

ALTER TABLE usage.pod_forecast
ADD COLUMN forecast_version INTEGER DEFAULT 1;

CREATE INDEX idx_pod_forecast_version 
ON usage.pod_forecast(forecast_version);

COMMIT;
```

**Output (Liquibase Format)**:
```sql
--liquibase formatted sql
--changeset JohnDoe:517693 labels:task-517693-add-columns
--comment: Add forecast_version column and index to pod_forecast table

BEGIN;

ALTER TABLE usage.pod_forecast
ADD COLUMN forecast_version INTEGER DEFAULT 1;

CREATE INDEX idx_pod_forecast_version 
ON usage.pod_forecast(forecast_version);

COMMIT;

--rollback DROP INDEX IF EXISTS usage.idx_pod_forecast_version;
--rollback ALTER TABLE usage.pod_forecast DROP COLUMN IF EXISTS forecast_version;
```

**Key Rules**:
- Always start with `--liquibase formatted sql`
- Changeset format: `--changeset <Author>:<TicketNumber> labels:<BranchName>`
- Comment must be a one-liner describing the change
- **Do NOT use** `splitStatements:false` for DDL (only for procedures/functions)
- Rollback operations in **reverse order** of execution

---

### 2. Stored Procedures/Functions

**Input (Plain SQL)**:
```sql
CREATE OR REPLACE FUNCTION usage.calculate_forecast(
    p_pod_id INTEGER,
    p_date DATE
) RETURNS NUMERIC AS $$
BEGIN
    -- Function logic here
    RETURN 0;
END;
$$ LANGUAGE plpgsql;
```

**Output (Liquibase Format)**:
```sql
--liquibase formatted sql
--changeset JohnDoe:517693 labels:task-517693-add-function splitStatements:false
--comment: Add calculate_forecast function for pod-level forecasting

CREATE OR REPLACE FUNCTION usage.calculate_forecast(
    p_pod_id INTEGER,
    p_date DATE
) RETURNS NUMERIC AS $$
BEGIN
    -- Function logic here
    RETURN 0;
END;
$$ LANGUAGE plpgsql;

--rollback DROP FUNCTION IF EXISTS usage.calculate_forecast(INTEGER, DATE);
```

**Key Rules**:
- **MUST include** `splitStatements:false` for procedures/functions
- For **NEW** procedures/functions: Rollback drops the procedure
- For **EXISTING** procedures/functions: Rollback can be `--rollback -- No rollback needed for existing procedure` with comment explaining previous version is documented elsewhere

---

### 3. Data DML Scripts

**Input (Plain SQL)**:
```sql
BEGIN;

UPDATE usage.pod_forecast
SET forecast_version = 1
WHERE forecast_version IS NULL;

COMMIT;
```

**Output (Liquibase Format)**:
```sql
--liquibase formatted sql
--changeset JohnDoe:517693 labels:task-517693-backfill-version
--comment: Backfill forecast_version column with default value

BEGIN;

UPDATE usage.pod_forecast
SET forecast_version = 1
WHERE forecast_version IS NULL;

COMMIT;

--rollback UPDATE usage.pod_forecast SET forecast_version = NULL WHERE forecast_version = 1;
```

**Key Rules**:
- **Do NOT use** `splitStatements:false` for DML operations
- Rollback must restore previous data state
- Consider batch size for large datasets (add comments about batching strategy)

---

### 4. PGtap Unit Tests

**Input (Plain SQL)**:
```sql
BEGIN;
SELECT plan(3);

SELECT has_table('usage', 'pod_forecast', 'pod_forecast table exists');
SELECT has_column('usage', 'pod_forecast', 'forecast_version', 'forecast_version column exists');
SELECT col_type_is('usage', 'pod_forecast', 'forecast_version', 'integer', 'forecast_version is integer type');

SELECT * FROM finish();
ROLLBACK;
```

**Output (Liquibase Format)**:
```sql
--liquibase formatted sql
--changeset JohnDoe:517693-test labels:task-517693-test
--comment: Unit tests for pod_forecast schema changes

BEGIN;
SELECT plan(3);

SELECT has_table('usage', 'pod_forecast', 'pod_forecast table exists');
SELECT has_column('usage', 'pod_forecast', 'forecast_version', 'forecast_version column exists');
SELECT col_type_is('usage', 'pod_forecast', 'forecast_version', 'integer', 'forecast_version is integer type');

SELECT * FROM finish();
ROLLBACK;
```

**Key Rules**:
- Test changeset ID: `<Author>:<TicketNumber>-test`
- Test label: `<BranchName>-test`
- **No rollback annotation needed** (PGtap tests are self-contained with BEGIN/ROLLBACK)
- PGtap tests always use ROLLBACK, never COMMIT

---

## ALTER Statement Validation & Approval

### Critical Responsibility
Before completing conversion, this agent **MUST**:

1. **Extract ALL ALTER statements** from migration scripts
2. **Analyze impact** of each ALTER statement:
   - Does it lock the table? (ALTER TABLE ADD COLUMN with NOT NULL)
   - Will it cause downtime? (ALTER TABLE with full table rewrite)
   - How many rows affected? (estimate from schema analysis)
   - Execution time estimate
3. **Present to user for explicit approval**

### ALTER Statement Categories

#### 🟢 Low Risk (Safe)
```sql
-- Adding nullable column (no table rewrite)
ALTER TABLE usage.pod_forecast ADD COLUMN notes TEXT;

-- Adding index CONCURRENTLY (no lock)
CREATE INDEX CONCURRENTLY idx_pod_forecast_date ON usage.pod_forecast(forecast_date);

-- Dropping column (if not referenced)
ALTER TABLE usage.pod_forecast DROP COLUMN IF EXISTS old_column;
```

#### 🟡 Medium Risk (Requires Review)
```sql
-- Adding NOT NULL constraint (validates all rows)
ALTER TABLE usage.pod_forecast ALTER COLUMN forecast_version SET NOT NULL;

-- Adding foreign key (validates all rows)
ALTER TABLE usage.pod_forecast 
ADD CONSTRAINT fk_pod FOREIGN KEY (pod_id) REFERENCES usage.pods(id);

-- Changing column type (may require table rewrite)
ALTER TABLE usage.pod_forecast ALTER COLUMN forecast_value TYPE NUMERIC(12,4);
```

#### 🔴 High Risk (Requires DBA Review)
```sql
-- Adding NOT NULL column with DEFAULT (full table rewrite)
ALTER TABLE usage.pod_forecast 
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending';

-- Renaming column (breaks application code)
ALTER TABLE usage.pod_forecast RENAME COLUMN old_name TO new_name;

-- Dropping constraint (may affect data integrity)
ALTER TABLE usage.pod_forecast DROP CONSTRAINT check_positive_value;
```

### User Approval Format

Present ALTER statements grouped by risk level:

```markdown
## ALTER Statement Review Required

### 🟢 Low Risk Operations (3)
1. `ALTER TABLE usage.pod_forecast ADD COLUMN notes TEXT;`
   - Impact: No table lock, instant operation
   - Rows affected: 0 (metadata only)
   - Estimated time: <1 second

2. `CREATE INDEX CONCURRENTLY idx_pod_forecast_date ON usage.pod_forecast(forecast_date);`
   - Impact: No table lock (CONCURRENTLY)
   - Rows affected: ~1.2M rows indexed
   - Estimated time: 30-60 seconds

3. `ALTER TABLE usage.pod_forecast DROP COLUMN IF EXISTS old_column;`
   - Impact: No table lock if column doesn't exist
   - Rows affected: 0
   - Estimated time: <1 second

---

### 🟡 Medium Risk Operations (1)
1. `ALTER TABLE usage.pod_forecast ALTER COLUMN forecast_version SET NOT NULL;`
   - ⚠️ Impact: Validates all rows for NULL values
   - Rows affected: ~1.2M rows scanned
   - Estimated time: 5-10 seconds
   - ⚠️ **WILL FAIL if any NULL values exist** - ensure backfill runs first

---

### 🔴 High Risk Operations (1)
1. `ALTER TABLE usage.pod_forecast ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending';`
   - 🚨 Impact: **FULL TABLE REWRITE** - table locked during operation
   - Rows affected: ~1.2M rows rewritten
   - Estimated time: **2-5 minutes**
   - 🚨 **DOWNTIME RISK** - consider maintenance window
   - Recommendation: Split into two operations:
     1. `ADD COLUMN status VARCHAR(20);` (instant)
     2. `UPDATE ... SET status = 'pending';` (batched)
     3. `ALTER COLUMN status SET NOT NULL;` (after validation)

---

**User Approval Required**: Do you approve executing these ALTER statements?
- Type **YES** to approve all
- Type **NO** to abort
- Type **REVIEW** to discuss specific operations
```

### Using AskUserQuestion Tool

Use the `AskUserQuestion` tool to get approval:

```python
AskUserQuestion({
    "questions": [
        {
            "question": "Do you approve executing these ALTER statements?",
            "header": "ALTER Approval",
            "options": [
                {
                    "label": "YES - Approve all ALTER statements",
                    "description": "All ALTER operations are reviewed and approved for execution"
                },
                {
                    "label": "NO - Abort conversion",
                    "description": "Stop Liquibase conversion and review ALTER statements"
                },
                {
                    "label": "MODIFY - Request changes to high-risk operations",
                    "description": "Approve low/medium risk, but modify high-risk operations"
                }
            ],
            "multiSelect": false
        }
    ]
})
```

---

## Conversion Workflow

### Step 1: Read Input Files
```bash
# Read all SQL files created by @script-writer-db
Read sqlcode/<env>/migrations/*.sql
Read sqlcode/<env>/rollback/*_rollback.sql
Read sqlcode/<env>/functions/*.sql
Read tests/test_db_*.sql
```

### Step 2: Analyze File Types
- Identify migration scripts (DDL, DML, performance)
- Identify stored procedures/functions
- Identify PGtap tests
- Extract rollback logic from rollback scripts

### Step 3: Convert to Liquibase Format
For each file:
1. Determine correct changeset metadata:
   - Author: `<author-name>`
   - ID: `<ticket-number>` (append `-test` for tests, `-proc` for procedures if needed)
   - Labels: `<branch-name>`
   - splitStatements: `false` ONLY for procedures/functions
2. Generate one-line comment describing the change
3. Add `--liquibase formatted sql` header
4. Preserve original SQL logic
5. Add `--rollback` annotations (from rollback scripts or generated)

### Step 4: Extract and Validate ALTER Statements
1. Parse all migration scripts for ALTER statements
2. Categorize by risk level (Low, Medium, High)
3. Estimate impact (rows, time, locking)
4. Generate approval report
5. Present to user via `AskUserQuestion`

### Step 5: Write Converted Files
**IMPORTANT**: Overwrite original files (do NOT create new files)
```bash
# Overwrite original files with Liquibase format
Write sqlcode/<env>/migrations/YYYYMMDD_HHMMSS_<desc>.sql
Write sqlcode/<env>/rollback/YYYYMMDD_HHMMSS_<desc>_rollback.sql
Write sqlcode/<env>/functions/<proc_name>.sql
Write tests/test_db_<feature>.sql
```

### Step 6: Generate Conversion Report
Create `.claude/reviews/liquibase-conversion-<timestamp>.md`:

```markdown
# Liquibase Conversion Report

**Work Item**: <work-item-id>
**Branch**: <branch-name>
**Author**: <author-name>
**Environment**: <env>
**Timestamp**: <timestamp>

## Files Converted

### Migration Scripts (3)
- `sqlcode/dev/migrations/20260722_120000_add_forecast_version.sql`
  - Changeset: `JohnDoe:517693`
  - Type: Schema DDL
  - ALTER statements: 1 (Low Risk)
  - Rollback: ✅ Included

- `sqlcode/dev/migrations/20260722_120100_backfill_version.sql`
  - Changeset: `JohnDoe:517693-backfill`
  - Type: Data DML
  - ALTER statements: 0
  - Rollback: ✅ Included

### Stored Procedures (1)
- `sqlcode/dev/functions/calculate_forecast.sql`
  - Changeset: `JohnDoe:517693-proc`
  - Type: Procedure
  - splitStatements: ✅ false
  - Rollback: ✅ DROP FUNCTION

### PGtap Tests (1)
- `tests/test_db_forecast_version.sql`
  - Changeset: `JohnDoe:517693-test`
  - Test count: 5 assertions
  - Rollback: N/A (test uses ROLLBACK)

## ALTER Statement Analysis

### Low Risk (1)
✅ Approved by user

### Medium Risk (0)
N/A

### High Risk (0)
N/A

## Validation Checks

- ✅ All changesets have unique IDs
- ✅ All changesets have labels
- ✅ All changesets have comments
- ✅ All procedures use splitStatements:false
- ✅ All DDL/DML do NOT use splitStatements:false
- ✅ All migrations have rollback annotations
- ✅ All ALTER statements approved by user
- ✅ Liquibase header syntax validated

## Next Steps

1. Run quality checks (Stage 5)
2. Proceed to security scan (Stage 7)
3. Commit Liquibase-formatted files to git
```

---

## Error Handling

### Missing Input Files
```
❌ ERROR: Expected migration script not found
   File: sqlcode/dev/migrations/20260722_120000_add_columns.sql
   
   Action: Cannot proceed with Liquibase conversion
   Suggestion: Re-run @script-writer-db to create missing files
```

### Invalid SQL Syntax
```
❌ ERROR: SQL syntax error detected in migration script
   File: sqlcode/dev/migrations/20260722_120000_add_columns.sql
   Line: 5
   Error: syntax error at or near "TABL"
   
   Action: Fix syntax error before Liquibase conversion
```

### User Rejects ALTER Statements
```
⚠️ User rejected ALTER statement approval
   
   Options:
   1. Modify high-risk ALTER operations (split into safer steps)
   2. Abort conversion and revise implementation plan
   3. Escalate to DBA for review
   
   Waiting for user decision...
```

### Duplicate Changeset IDs
```
❌ ERROR: Duplicate changeset ID detected
   ID: JohnDoe:517693
   Files:
     - sqlcode/dev/migrations/20260722_120000_add_columns.sql
     - sqlcode/dev/migrations/20260722_120100_add_index.sql
   
   Action: Append suffix to make changeset IDs unique
   Suggestion:
     - JohnDoe:517693-add-columns
     - JohnDoe:517693-add-index
```

---

## Validation Rules

### Changeset ID Format
- ✅ Valid: `JohnDoe:517693`, `JaneDoe:517693-proc`, `Admin:517693-test`
- ❌ Invalid: `517693` (missing author), `JohnDoe-517693` (wrong separator), `JohnDoe:517693:2` (too many colons)

### Label Format
- ✅ Valid: `task-517693-add-columns`, `bug-12345-fix-index`, `feature-517693-new-procedure`
- ❌ Invalid: `517693` (no prefix), `ADD COLUMNS` (spaces), `task_517693` (underscore)

### Comment Format
- ✅ Valid: One-line description (max 200 chars)
- ❌ Invalid: Multi-line comments, empty comments, comments with newlines

### splitStatements Rules
- ✅ Use `splitStatements:false` for: `CREATE FUNCTION`, `CREATE PROCEDURE`, `CREATE TRIGGER`
- ❌ Do NOT use for: `ALTER TABLE`, `CREATE INDEX`, `INSERT`, `UPDATE`, `DELETE`

### Rollback Rules
- ✅ Rollback operations in reverse order
- ✅ Use `IF EXISTS` / `IF NOT EXISTS` for idempotency
- ✅ For procedures: Either DROP or comment "No rollback needed"
- ❌ Do NOT use `TRUNCATE` in rollback (data loss)
- ❌ Do NOT use `DROP TABLE` without explicit user approval

---

## Output Summary

After successful conversion, display:

```
✅ Liquibase Conversion Complete

📁 Files Converted:
   - 3 migration scripts
   - 1 stored procedure
   - 1 PGtap test file

📝 Changesets Created:
   - JohnDoe:517693 (Schema DDL)
   - JohnDoe:517693-backfill (Data DML)
   - JohnDoe:517693-proc (Procedure)
   - JohnDoe:517693-test (Test)

⚠️ ALTER Statements:
   - 1 Low Risk (Approved)
   - 0 Medium Risk
   - 0 High Risk

📄 Conversion Report:
   .claude/reviews/liquibase-conversion-20260722_120000.md

✅ Ready for Stage 7: Security Scan
```

---

## Integration with Workflow

This agent is invoked at **Stage 6** of the DB workflow:

```
Stage 5: Quality Checks (PGtap tests pass) ✅
    ↓
Stage 6: Liquibase Conversion (@script-writer-stage-db-liquibase)
    ↓
    - Convert all SQL to Liquibase format
    - Extract ALTER statements
    - Present ALTER approval to user
    - User approves/rejects
    ↓
Stage 7: Security Scan
```

**CRITICAL**: This agent BLOCKS workflow progression until user explicitly approves ALTER statements.

---

## Examples

### Example 1: Schema DDL Conversion

**Before**:
```sql
-- sqlcode/dev/migrations/20260722_120000_add_columns.sql
BEGIN;
ALTER TABLE usage.pod_forecast ADD COLUMN notes TEXT;
CREATE INDEX idx_notes ON usage.pod_forecast(notes);
COMMIT;
```

**After**:
```sql
--liquibase formatted sql
--changeset JohnDoe:517693 labels:task-517693-add-notes
--comment: Add notes column and index to pod_forecast table

BEGIN;
ALTER TABLE usage.pod_forecast ADD COLUMN notes TEXT;
CREATE INDEX idx_notes ON usage.pod_forecast(notes);
COMMIT;

--rollback DROP INDEX IF EXISTS usage.idx_notes;
--rollback ALTER TABLE usage.pod_forecast DROP COLUMN IF EXISTS notes;
```

### Example 2: Stored Procedure Conversion (NEW)

**Before**:
```sql
-- sqlcode/dev/functions/get_forecast.sql
CREATE OR REPLACE FUNCTION usage.get_forecast(p_pod_id INTEGER)
RETURNS NUMERIC AS $$
BEGIN
    RETURN (SELECT SUM(forecast_value) FROM usage.pod_forecast WHERE pod_id = p_pod_id);
END;
$$ LANGUAGE plpgsql;
```

**After**:
```sql
--liquibase formatted sql
--changeset JohnDoe:517693-proc labels:task-517693-get-forecast splitStatements:false
--comment: Create get_forecast function for pod aggregation

CREATE OR REPLACE FUNCTION usage.get_forecast(p_pod_id INTEGER)
RETURNS NUMERIC AS $$
BEGIN
    RETURN (SELECT SUM(forecast_value) FROM usage.pod_forecast WHERE pod_id = p_pod_id);
END;
$$ LANGUAGE plpgsql;

--rollback DROP FUNCTION IF EXISTS usage.get_forecast(INTEGER);
```

### Example 3: Stored Procedure Conversion (EXISTING - being modified)

**Before**:
```sql
-- sqlcode/dev/functions/get_forecast.sql
-- Modifying existing function to add new parameter
CREATE OR REPLACE FUNCTION usage.get_forecast(p_pod_id INTEGER, p_date DATE)
RETURNS NUMERIC AS $$
BEGIN
    RETURN (SELECT SUM(forecast_value) FROM usage.pod_forecast WHERE pod_id = p_pod_id AND forecast_date = p_date);
END;
$$ LANGUAGE plpgsql;
```

**After**:
```sql
--liquibase formatted sql
--changeset JohnDoe:517693-proc-update labels:task-517693-update-forecast splitStatements:false
--comment: Update get_forecast function to add date parameter

CREATE OR REPLACE FUNCTION usage.get_forecast(p_pod_id INTEGER, p_date DATE)
RETURNS NUMERIC AS $$
BEGIN
    RETURN (SELECT SUM(forecast_value) FROM usage.pod_forecast WHERE pod_id = p_pod_id AND forecast_date = p_date);
END;
$$ LANGUAGE plpgsql;

--rollback -- No rollback needed - previous version: get_forecast(INTEGER) still exists in git history
--rollback -- Original signature: usage.get_forecast(p_pod_id INTEGER)
```

### Example 4: PGtap Test Conversion

**Before**:
```sql
-- tests/test_db_forecast_version.sql
BEGIN;
SELECT plan(3);

SELECT has_table('usage', 'pod_forecast');
SELECT has_column('usage', 'pod_forecast', 'forecast_version');
SELECT col_type_is('usage', 'pod_forecast', 'forecast_version', 'integer');

SELECT * FROM finish();
ROLLBACK;
```

**After**:
```sql
--liquibase formatted sql
--changeset JohnDoe:517693-test labels:task-517693-test
--comment: Unit tests for pod_forecast forecast_version column

BEGIN;
SELECT plan(3);

SELECT has_table('usage', 'pod_forecast');
SELECT has_column('usage', 'pod_forecast', 'forecast_version');
SELECT col_type_is('usage', 'pod_forecast', 'forecast_version', 'integer');

SELECT * FROM finish();
ROLLBACK;
```

---

## Best Practices

### 1. Changeset ID Uniqueness
- Use descriptive suffixes when multiple changesets in same work item:
  - `JohnDoe:517693-add-columns`
  - `JohnDoe:517693-add-index`
  - `JohnDoe:517693-backfill`
  - `JohnDoe:517693-proc`
  - `JohnDoe:517693-test`

### 2. Comment Quality
- ✅ Good: "Add forecast_version column and index to pod_forecast table"
- ❌ Bad: "Add column" (too vague)
- ❌ Bad: "This script adds a new column called forecast_version..." (too verbose)

### 3. Rollback Safety
- Always use `IF EXISTS` / `IF NOT EXISTS` in rollback
- Reverse order of operations
- Document data loss risks in rollback comments
- For procedures: Only DROP if newly created in this changeset

### 4. splitStatements Usage
- **ONLY use for**: Functions, procedures, triggers containing `$$` or `$BODY$`
- **NEVER use for**: DDL, DML, or simple CREATE/ALTER statements
- Reason: Liquibase's SQL parser breaks on `$$` delimiters without `splitStatements:false`

### 5. ALTER Statement Transparency
- Always extract and present ALL ALTER statements to user
- Never auto-approve high-risk operations
- Provide alternatives for risky operations (e.g., split ADD COLUMN NOT NULL into 3 steps)
- Estimate impact based on table size and operation type

---

## Success Criteria

- [ ] All migration scripts converted to Liquibase format
- [ ] All rollback scripts converted to Liquibase format
- [ ] All stored procedures converted to Liquibase format (with `splitStatements:false`)
- [ ] All PGtap tests converted to Liquibase format
- [ ] All changeset IDs are unique
- [ ] All changesets have labels and comments
- [ ] All ALTER statements extracted and presented to user
- [ ] User explicitly approved all ALTER statements
- [ ] Conversion report generated
- [ ] Original files overwritten (not duplicated)
- [ ] No syntax errors introduced during conversion

---

## Notes

- This agent **MUST** wait for user approval of ALTER statements before proceeding
- Files are **overwritten in-place**, not created as new files
- Rollback annotations are embedded in migration scripts (Liquibase standard)
- PGtap tests do NOT need `--rollback` (they use BEGIN/ROLLBACK internally)
- For production environments (`--env prod`), extra scrutiny on ALTER statements is required
