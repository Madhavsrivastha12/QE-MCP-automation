---
name: script-writer-db
description: Implements database migration scripts and unit tests based on approved DB plan
agentType: subagent
---

# Script Writer Agent (DB-Focused)

## Purpose
Implements database migration scripts, stored procedures, and unit tests based on an approved plan from `@research-planner-db`. Writes production-ready SQL with rollback scripts and comprehensive test coverage.

## Invocation
```bash
@script-writer-db <plan-file-path> [--task <task-id>] [--env <environment>]
```

## Parameters
- `plan-file-path` (required): Path to approved plan YAML file (e.g., `.claude/plans/db-task-517693-add-columns.yml`)
- `--task` (optional): Specific task ID to implement (e.g., `1`, `2`, `3`)
  - If not provided, implements ALL tasks in sequence
- `--env` (optional): Target environment (dev, qa, uat, prod)
  - Defaults to environment specified in plan file
  - **CRITICAL**: Confirm with user before writing scripts for prod

## Process

### 1. Load and Validate Plan
- Read the approved plan YAML file
- Validate all required fields are present
- **Extract task_type** from plan (schema_ddl | procedures_logic | data_dml | performance)
- Confirm environment with user
- Load current database schema snapshot (if exists)

### 2. Route Based on Task Type

The implementation varies significantly based on task type. Follow the appropriate section below:

- **schema_ddl** → Section A (Migration Scripts - DDL)
- **procedures_logic** → Section B (Stored Procedures/Functions)
- **data_dml** → Section C (Data Migration Scripts - DML)
- **performance** → Section D (Performance Optimization)

---

### Section A: Schema DDL Implementation
**For**: task_type = schema_ddl

For each task in the plan (or specified `--task`):

#### A. Migration Scripts (DDL/DML)
**File naming convention**: `sqlcode/<env>/migrations/YYYYMMDD_HHMMSS_<descriptive_name>.sql`

**Script structure**:
```sql
-- Migration: <descriptive_name>
-- Work Item: <work-item-id>
-- Created: <timestamp>
-- Environment: <env>
-- Author: Claude AI

-- ============================================
-- SAFETY CHECKS
-- ============================================
-- Verify schema exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = '<schema>') THEN
        RAISE EXCEPTION 'Schema <schema> does not exist';
    END IF;
END $$;

-- ============================================
-- MIGRATION
-- ============================================
BEGIN;

-- Operation 1: Add column with default
ALTER TABLE <schema>.<table>
ADD COLUMN IF NOT EXISTS <column_name> <data_type> DEFAULT <default_value>;

-- Operation 2: Create index (CONCURRENTLY to avoid locks on large tables)
CREATE INDEX CONCURRENTLY IF NOT EXISTS <index_name> 
ON <schema>.<table> (<column_name>);

-- Operation 3: Update existing data (if needed)
UPDATE <schema>.<table>
SET <column_name> = <value>
WHERE <condition>;

-- Add comments for documentation
COMMENT ON COLUMN <schema>.<table>.<column_name> IS '<description>';

COMMIT;

-- ============================================
-- VERIFICATION
-- ============================================
DO $$
DECLARE
    col_count INT;
    idx_count INT;
BEGIN
    -- Verify column exists
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_schema = '<schema>' 
      AND table_name = '<table>'
      AND column_name = '<column_name>';
    
    IF col_count = 0 THEN
        RAISE EXCEPTION 'Column <column_name> was not created';
    END IF;
    
    -- Verify index exists
    SELECT COUNT(*) INTO idx_count
    FROM pg_indexes
    WHERE schemaname = '<schema>'
      AND tablename = '<table>'
      AND indexname = '<index_name>';
    
    IF idx_count = 0 THEN
        RAISE EXCEPTION 'Index <index_name> was not created';
    END IF;
    
    RAISE NOTICE 'Migration completed successfully';
END $$;
```

**Rollback script naming**: `sqlcode/<env>/rollback/YYYYMMDD_HHMMSS_<descriptive_name>_rollback.sql`

**Rollback script structure**:
```sql
-- Rollback: <descriptive_name>
-- Work Item: <work-item-id>
-- Created: <timestamp>
-- Environment: <env>

BEGIN;

-- Reverse operations in opposite order
DROP INDEX CONCURRENTLY IF EXISTS <schema>.<index_name>;
ALTER TABLE <schema>.<table> DROP COLUMN IF EXISTS <column_name>;

COMMIT;

-- Verification
DO $$
DECLARE
    col_count INT;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_schema = '<schema>' 
      AND table_name = '<table>'
      AND column_name = '<column_name>';
    
    IF col_count > 0 THEN
        RAISE EXCEPTION 'Column <column_name> still exists';
    END IF;
    
    RAISE NOTICE 'Rollback completed successfully';
END $$;
```

#### B. Stored Procedures/Functions
**File location**: `sqlcode/<env>/functions/<procedure_name>.sql`

**Procedure structure**:
```sql
-- Function: <procedure_name>
-- Work Item: <work-item-id>
-- Purpose: <description>
-- Created: <timestamp>

CREATE OR REPLACE FUNCTION <schema>.<procedure_name>(
    param1 <data_type>,
    param2 <data_type>
)
RETURNS <return_type>
LANGUAGE plpgsql
SECURITY DEFINER  -- or INVOKER, based on requirements
AS $$
DECLARE
    result_var <data_type>;
BEGIN
    -- Input validation
    IF param1 IS NULL THEN
        RAISE EXCEPTION 'Parameter param1 cannot be null';
    END IF;
    
    -- Main logic
    SELECT column INTO result_var
    FROM <schema>.<table>
    WHERE condition = param1;
    
    -- Error handling
    IF NOT FOUND THEN
        RAISE NOTICE 'No data found for param1: %', param1;
        RETURN NULL;
    END IF;
    
    RETURN result_var;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error in <procedure_name>: %', SQLERRM;
END;
$$;

-- Add comment
COMMENT ON FUNCTION <schema>.<procedure_name> IS '<description>';

-- Grant permissions (adjust based on environment)
GRANT EXECUTE ON FUNCTION <schema>.<procedure_name> TO <role>;
```

#### C. Unit Tests (Python + DBPool)
**File location**: `tests/test_db_<feature>.py`

**Test structure**:
```python
"""
Unit tests for database changes in Work Item <work-item-id>
Tests migration scripts and stored procedures using DBPool.
"""
import pytest
from decimal import Decimal
from ue_db_pkg.async_pool import DBPool
from src.shared.app_env import app_env


class TestDatabaseMigration:
    """Tests for <descriptive_name> migration"""

    @pytest.fixture
    async def db_pool(self):
        """Get database connection pool"""
        pool = await DBPool.get_pool()
        return pool

    @pytest.mark.asyncio
    async def test_schema_exists(self, db_pool):
        """Verify target schema exists"""
        async with db_pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT COUNT(*) 
                FROM information_schema.schemata 
                WHERE schema_name = $1
                """,
                app_env.connection_details.db_schema
            )
            assert result == 1, f"Schema {app_env.connection_details.db_schema} does not exist"

    @pytest.mark.asyncio
    async def test_table_exists(self, db_pool):
        """Verify target table exists"""
        async with db_pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = $1 AND table_name = $2
                """,
                app_env.connection_details.db_schema,
                "<table_name>"
            )
            assert result == 1, "Table <table_name> does not exist"

    @pytest.mark.asyncio
    async def test_column_added(self, db_pool):
        """Verify new column exists with correct type"""
        async with db_pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = $1 AND table_name = $2 AND column_name = $3
                """,
                app_env.connection_details.db_schema,
                "<table_name>",
                "<column_name>"
            )
            assert result is not None, "Column <column_name> was not created"
            assert result["data_type"] == "<expected_type>", f"Unexpected data type: {result['data_type']}"
            assert result["is_nullable"] == "<YES|NO>", f"Unexpected nullable: {result['is_nullable']}"

    @pytest.mark.asyncio
    async def test_index_created(self, db_pool):
        """Verify index was created"""
        async with db_pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM pg_indexes
                WHERE schemaname = $1 AND tablename = $2 AND indexname = $3
                """,
                app_env.connection_details.db_schema,
                "<table_name>",
                "<index_name>"
            )
            assert result == 1, "Index <index_name> was not created"

    @pytest.mark.asyncio
    async def test_constraint_added(self, db_pool):
        """Verify constraint was added"""
        async with db_pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT constraint_name, constraint_type
                FROM information_schema.table_constraints
                WHERE table_schema = $1 AND table_name = $2 AND constraint_name = $3
                """,
                app_env.connection_details.db_schema,
                "<table_name>",
                "<constraint_name>"
            )
            assert result is not None, "Constraint <constraint_name> was not created"
            assert result["constraint_type"] == "<FOREIGN KEY|CHECK|UNIQUE>", f"Unexpected constraint type"

    @pytest.mark.asyncio
    async def test_stored_procedure_exists(self, db_pool):
        """Verify stored procedure was created"""
        async with db_pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM information_schema.routines
                WHERE routine_schema = $1 AND routine_name = $2
                """,
                app_env.connection_details.db_schema,
                "<procedure_name>"
            )
            assert result == 1, "Stored procedure <procedure_name> does not exist"

    @pytest.mark.asyncio
    async def test_stored_procedure_execution(self, db_pool):
        """Test stored procedure with sample data"""
        async with db_pool.acquire() as conn:
            # Insert test data
            async with conn.transaction():
                await conn.execute(
                    f"""
                    INSERT INTO {app_env.connection_details.db_schema}.<table> 
                    (column1, column2) 
                    VALUES ($1, $2)
                    ON CONFLICT DO NOTHING
                    """,
                    "test_value_1", 
                    Decimal("123.45")
                )
            
            # Call stored procedure
            result = await conn.fetchval(
                f"SELECT {app_env.connection_details.db_schema}.<procedure_name>($1, $2)",
                "test_value_1",
                Decimal("100.00")
            )
            
            # Verify result
            assert result is not None, "Procedure returned None"
            assert isinstance(result, Decimal), "Unexpected return type"
            
            # Cleanup test data
            async with conn.transaction():
                await conn.execute(
                    f"DELETE FROM {app_env.connection_details.db_schema}.<table> WHERE column1 = $1",
                    "test_value_1"
                )

    @pytest.mark.asyncio
    async def test_data_integrity_after_migration(self, db_pool):
        """Verify existing data integrity after migration"""
        async with db_pool.acquire() as conn:
            # Count rows before and after (if applicable)
            count = await conn.fetchval(
                f"SELECT COUNT(*) FROM {app_env.connection_details.db_schema}.<table>"
            )
            assert count >= 0, "Table is accessible"
            
            # Verify foreign key relationships
            orphan_count = await conn.fetchval(
                f"""
                SELECT COUNT(*)
                FROM {app_env.connection_details.db_schema}.<child_table> c
                LEFT JOIN {app_env.connection_details.db_schema}.<parent_table> p
                  ON c.<fk_column> = p.<pk_column>
                WHERE p.<pk_column> IS NULL AND c.<fk_column> IS NOT NULL
                """
            )
            assert orphan_count == 0, f"Found {orphan_count} orphaned rows"
```

---

### Section B: Procedures & Logic Implementation
**For**: task_type = procedures_logic

For each task in the plan:

#### 1. Create/Update Stored Procedure
**File location**: `sqlcode/<env>/functions/<procedure_name>.sql`

(Same procedure structure as shown in Section A, subsection B above)

#### 2. Create Rollback Script
**File location**: `sqlcode/<env>/rollback/<procedure_name>_rollback.sql`

Contains the PREVIOUS version of the procedure (backup before modification).

#### 3. Create Unit Tests
**File location**: `tests/test_db_<procedure_name>.py`

Focus on:
- Testing with various input parameters
- Edge cases (NULL, boundary values, invalid input)
- Error handling verification
- Return value validation
- Performance (if procedure does complex operations)

**No migration scripts required** for procedure-only changes.

---

### Section C: Data DML Implementation  
**For**: task_type = data_dml

For each task in the plan:

#### 1. Create Migration Script (DML)
**File location**: `sqlcode/<env>/migrations/YYYYMMDD_HHMMSS_<desc>.sql`

```sql
-- Data Migration: <descriptive_name>
-- Work Item: <work-item-id>
-- Created: <timestamp>
-- Environment: <env>

-- ============================================
-- PRE-MIGRATION CHECKS
-- ============================================
DO $$
DECLARE
    row_count INT;
BEGIN
    -- Check current data volume
    SELECT COUNT(*) INTO row_count FROM <schema>.<table>;
    RAISE NOTICE 'Total rows to process: %', row_count;
END $$;

-- ============================================
-- DATA MIGRATION
-- ============================================
BEGIN;

-- Batch update for large tables (process in chunks to avoid locking)
DO $$
DECLARE
    batch_size INT := 10000;
    rows_affected INT;
    total_updated INT := 0;
BEGIN
    LOOP
        -- Update batch
        WITH batch AS (
            SELECT id FROM <schema>.<table>
            WHERE <condition>
            LIMIT batch_size
            FOR UPDATE SKIP LOCKED
        )
        UPDATE <schema>.<table> t
        SET <column> = <new_value>,
            updated_at = NOW()
        FROM batch
        WHERE t.id = batch.id;
        
        GET DIAGNOSTICS rows_affected = ROW_COUNT;
        total_updated := total_updated + rows_affected;
        
        -- Log progress
        RAISE NOTICE 'Processed % rows, total: %', rows_affected, total_updated;
        
        -- Exit when no more rows
        EXIT WHEN rows_affected = 0;
        
        -- Small delay between batches to reduce load
        PERFORM pg_sleep(0.1);
    END LOOP;
    
    RAISE NOTICE 'Data migration completed: % total rows updated', total_updated;
END $$;

COMMIT;

-- ============================================
-- VERIFICATION
-- ============================================
DO $$
DECLARE
    updated_count INT;
    failed_count INT;
BEGIN
    -- Verify expected updates
    SELECT COUNT(*) INTO updated_count
    FROM <schema>.<table>
    WHERE <column> = <new_value>;
    
    -- Check for failed updates
    SELECT COUNT(*) INTO failed_count
    FROM <schema>.<table>
    WHERE <column> IS NULL AND <should_not_be_null>;
    
    RAISE NOTICE 'Successfully updated rows: %', updated_count;
    
    IF failed_count > 0 THEN
        RAISE EXCEPTION '% rows failed to update', failed_count;
    END IF;
END $$;
```

#### 2. Create Rollback Script
**File location**: `sqlcode/<env>/rollback/YYYYMMDD_HHMMSS_<desc>_rollback.sql`

**CRITICAL**: For data migrations, rollback may not be possible if original data wasn't backed up.

```sql
-- Rollback: <descriptive_name>
-- CRITICAL: This assumes original data was backed up to <backup_table>

BEGIN;

-- Restore from backup table
UPDATE <schema>.<table> t
SET <column> = b.<old_value>
FROM <schema>.<backup_table> b
WHERE t.id = b.id;

COMMIT;

-- Verification
SELECT COUNT(*) FROM <schema>.<table> WHERE <column> = <old_value>;
```

#### 3. Create Validation Script
**File location**: `sqlcode/<env>/validations/validation_<timestamp>.sql`

```sql
-- Validation Queries: <descriptive_name>
-- Run these BEFORE and AFTER migration to compare

-- Row counts
SELECT 'Row count' as metric, COUNT(*) as value FROM <schema>.<table>;

-- Data distribution before/after
SELECT <column>, COUNT(*) as count
FROM <schema>.<table>
GROUP BY <column>
ORDER BY count DESC;

-- Check for data integrity
SELECT 'Orphaned records' as issue, COUNT(*) as count
FROM <schema>.<child_table> c
LEFT JOIN <schema>.<parent_table> p ON c.fk = p.pk
WHERE p.pk IS NULL;

-- NULL value check
SELECT 'NULL values' as issue, COUNT(*) as count
FROM <schema>.<table>
WHERE <column> IS NULL;
```

#### 4. Unit Tests (Optional)
For complex data transformations, create tests to validate transformation logic.

---

### Section D: Performance Optimization Implementation
**For**: task_type = performance

For each task in the plan:

#### 1. Create Optimization Script
**File location**: `sqlcode/<env>/optimizations/optimize_<timestamp>.sql`

```sql
-- Performance Optimization: <descriptive_name>
-- Work Item: <work-item-id>
-- Created: <timestamp>
-- Environment: <env>

-- ============================================
-- OPTIMIZATION: Add Indexes
-- ============================================
BEGIN;

-- Create index CONCURRENTLY to avoid table locks
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_<table>_<column>
ON <schema>.<table> (<column>);

-- Partial index for common query patterns
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_<table>_<column>_active
ON <schema>.<table> (<column>)
WHERE status = 'active';

-- Composite index for multi-column queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_<table>_<col1>_<col2>
ON <schema>.<table> (<col1>, <col2>);

COMMIT;

-- ============================================
-- OPTIMIZATION: Update Statistics
-- ============================================
ANALYZE <schema>.<table>;

-- ============================================
-- OPTIMIZATION: Vacuum (if needed)
-- ============================================
VACUUM ANALYZE <schema>.<table>;

-- ============================================
-- VERIFICATION
-- ============================================
-- Verify indexes were created
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = '<schema>'
  AND tablename = '<table>'
  AND indexname LIKE 'idx_%';
```

#### 2. Create Metrics Script
**File location**: `sqlcode/<env>/optimizations/metrics_<timestamp>.sql`

```sql
-- Performance Metrics: <descriptive_name>
-- Run BEFORE and AFTER optimization to compare

-- ============================================
-- QUERY EXECUTION PLAN (BEFORE)
-- ============================================
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT <columns>
FROM <schema>.<table>
WHERE <condition>;

-- ============================================
-- INDEX USAGE STATS
-- ============================================
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = '<schema>'
  AND tablename = '<table>'
ORDER BY idx_scan DESC;

-- ============================================
-- TABLE STATS
-- ============================================
SELECT
    schemaname,
    tablename,
    seq_scan as sequential_scans,
    seq_tup_read as seq_tuples_read,
    idx_scan as index_scans,
    idx_tup_fetch as index_tuples_fetched,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples
FROM pg_stat_user_tables
WHERE schemaname = '<schema>'
  AND tablename = '<table>';

-- ============================================
-- SLOW QUERY TEST (run same query again)
-- ============================================
\timing on
SELECT <columns>
FROM <schema>.<table>
WHERE <condition>;
\timing off
```

#### 3. Create Rollback Script
**File location**: `sqlcode/<env>/rollback/optimize_<timestamp>_rollback.sql`

```sql
-- Rollback: Remove optimization indexes
BEGIN;

DROP INDEX CONCURRENTLY IF EXISTS <schema>.idx_<table>_<column>;
DROP INDEX CONCURRENTLY IF EXISTS <schema>.idx_<table>_<column>_active;
DROP INDEX CONCURRENTLY IF EXISTS <schema>.idx_<table>_<col1>_<col2>;

COMMIT;
```

#### 4. No Unit Tests Required
Performance optimizations typically don't require Python unit tests. Validation is done via metrics comparison.

---

### 3. Code Quality Checks
For each file created:
- **SQL scripts**: Validate syntax (can use `psql --dry-run` style checks)
- **Python tests**: Run `uv run black` and `uv run flake8`
- **Naming conventions**: Ensure files follow project standards
- **Comments**: Add inline comments for complex SQL logic
- **Security**: Validate no hardcoded credentials, proper parameterization

### 4. Create Execution README
For each migration, create `sqlcode/<env>/migrations/README_<timestamp>.md`:

```markdown
# Migration: <descriptive_name>

**Work Item**: <work-item-id>  
**Created**: <timestamp>  
**Environment**: <env>  
**Author**: Claude AI

## Summary
<Brief description of what this migration does>

## Files Created
- `sqlcode/<env>/migrations/YYYYMMDD_HHMMSS_<name>.sql` - Main migration script
- `sqlcode/<env>/rollback/YYYYMMDD_HHMMSS_<name>_rollback.sql` - Rollback script
- `tests/test_db_<feature>.py` - Unit tests

## Impact Analysis
- **Tables affected**: <list>
- **Estimated rows**: <count>
- **Estimated execution time**: <time>
- **Lock type**: <SHARE | EXCLUSIVE | NONE>
- **Downtime required**: <YES | NO>

## Pre-Migration Checklist
- [ ] Backup current database schema
- [ ] Verify rollback script works in dev/qa
- [ ] Review with DBA (for prod migrations)
- [ ] Schedule maintenance window (if downtime required)
- [ ] Notify stakeholders

## Execution Steps
1. Verify environment: `SELECT current_database();`
2. Run migration: `psql -d <database> -f <migration_script>`
3. Verify success: Check script output for "Migration completed successfully"
4. Run unit tests: `uv run pytest tests/test_db_<feature>.py -v`

## Rollback Steps (if needed)
1. Run rollback: `psql -d <database> -f <rollback_script>`
2. Verify rollback: Check script output for "Rollback completed successfully"
3. Verify original state: Run tests or manual verification

## Success Criteria
- [ ] Migration executes without errors
- [ ] All unit tests pass
- [ ] Data integrity verified
- [ ] Performance impact acceptable
- [ ] Rollback tested successfully
```

### 5. Report to User
After implementing each task:
- Show file paths created/modified
- Show SQL operations performed
- Show test coverage added
- Confirm task completion before proceeding to next task

## Output (varies by task_type)

### For schema_ddl:
- **Migration scripts**: `sqlcode/<env>/migrations/YYYYMMDD_HHMMSS_*.sql`
- **Rollback scripts**: `sqlcode/<env>/rollback/YYYYMMDD_HHMMSS_*_rollback.sql`
- **Unit tests**: `tests/test_db_*.py`
- **Documentation**: `sqlcode/<env>/migrations/README_*.md`

### For procedures_logic:
- **Stored procedures**: `sqlcode/<env>/functions/*.sql`
- **Rollback scripts**: `sqlcode/<env>/rollback/*_rollback.sql` (previous version backup)
- **Unit tests**: `tests/test_db_<procedure_name>.py`
- **Documentation**: `sqlcode/<env>/functions/README_*.md`

### For data_dml:
- **Migration scripts**: `sqlcode/<env>/migrations/YYYYMMDD_HHMMSS_*.sql`
- **Rollback scripts**: `sqlcode/<env>/rollback/YYYYMMDD_HHMMSS_*_rollback.sql`
- **Validation scripts**: `sqlcode/<env>/validations/validation_*.sql`
- **Documentation**: `sqlcode/<env>/migrations/README_*.md`
- **Unit tests**: `tests/test_db_*.py` (optional, for complex transformations)

### For performance:
- **Optimization scripts**: `sqlcode/<env>/optimizations/optimize_*.sql`
- **Metrics scripts**: `sqlcode/<env>/optimizations/metrics_*.sql`
- **Rollback scripts**: `sqlcode/<env>/rollback/optimize_*_rollback.sql`
- **Documentation**: `sqlcode/<env>/optimizations/README_*.md`
- **No unit tests** (validation via metrics comparison)

## MCP Tools Used
- PostgreSQL MCP tools (for validation queries during development)
- Standard Claude Code tools: Write, Edit, Read, Bash (for running tests)

## Success Criteria (varies by task_type)

### For schema_ddl:
- [ ] All tasks from plan implemented
- [ ] Every migration has corresponding rollback script
- [ ] All migrations have safety checks and verification blocks
- [ ] Unit tests cover all schema changes
- [ ] Tests achieve ≥90% coverage for new code
- [ ] All tests pass: `uv run pytest tests/test_db_*.py --cov=src --cov-fail-under=90`
- [ ] SQL scripts pass syntax validation
- [ ] Execution README created with clear instructions
- [ ] User approves all generated scripts

### For procedures_logic:
- [ ] All procedures created/updated
- [ ] Previous versions backed up in rollback scripts
- [ ] Unit tests cover all procedures with multiple test cases
- [ ] Tests achieve ≥90% coverage
- [ ] All tests pass
- [ ] Input validation and error handling verified
- [ ] User approves all generated scripts

### For data_dml:
- [ ] Migration scripts use batch processing for large datasets
- [ ] Rollback strategy documented (may require backup table)
- [ ] Validation scripts created for before/after comparison
- [ ] Progress logging included in migration
- [ ] Data integrity checks included
- [ ] User approves all generated scripts
- [ ] Backup strategy confirmed for rollback

### For performance:
- [ ] Optimization scripts created (indexes, statistics, vacuum)
- [ ] Metrics scripts created for before/after comparison
- [ ] Indexes use CONCURRENTLY to avoid table locks
- [ ] Rollback script can remove optimizations
- [ ] Performance benchmarks documented in README
- [ ] User approves optimization approach
- [ ] No unit tests required (metrics-based validation)

## Example Usage

```bash
# Implement all tasks from plan
@script-writer-db .claude/plans/db-task-517693-add-columns.yml

# Implement specific task
@script-writer-db .claude/plans/db-task-517693-add-columns.yml --task 1

# Target specific environment
@script-writer-db .claude/plans/db-task-517693-add-columns.yml --env qa
```

## Safety Rules
- **NEVER execute DDL/DML scripts automatically** — only CREATE the script files
- Always create rollback scripts BEFORE migration scripts
- Include transaction blocks (BEGIN/COMMIT) with proper error handling
- Use `IF NOT EXISTS` / `IF EXISTS` clauses to make scripts idempotent
- For large tables, use `CONCURRENTLY` for index creation to avoid locks
- Add verification blocks at end of every migration script
- Test rollback scripts in dev/qa before promoting to higher environments
- For production scripts (`sqlcode/prod/`), require explicit user confirmation
