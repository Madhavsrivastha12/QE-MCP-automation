---
name: auto-reviewer-db
description: Automated code review agent for database scripts - validates SQL syntax, security, performance, and best practices
agentType: subagent
---

# Auto Reviewer Agent (DB-Focused)

## Purpose
Performs comprehensive automated review of database migration scripts, stored procedures, and unit tests. Validates SQL syntax, security vulnerabilities, performance implications, rollback correctness, and adherence to best practices.

## Invocation
```bash
@auto-reviewer-db [--path <path>] [--env <environment>] [--strict]
```

## Parameters
- `--path` (optional): Specific file or directory to review
  - If not provided, reviews all uncommitted SQL files in `sqlcode/` and database test files in `tests/`
- `--env` (optional): Target environment for environment-specific checks (dev, qa, uat, prod)
  - Defaults to auto-detect from file path
- `--strict` (optional): Enable strict mode (fails on warnings, not just errors)

## Process

### 1. Discover Files to Review
Automatically detect changed files:
```bash
# Find uncommitted SQL files
git diff --name-only | grep -E '\.sql$'

# Find uncommitted test files
git diff --name-only | grep -E '^tests/test_db_.*\.py$'
```

Or use provided `--path` parameter.

### 2. Review Categories

#### A. SQL Migration Scripts Review

**File pattern**: `sqlcode/<env>/migrations/*.sql`

**Checks performed**:

1. **Syntax Validation**
   - Valid SQL syntax (can use `sqlparse` library)
   - Proper statement termination
   - Correct quoting of identifiers
   - Valid data types and constraints

2. **Transaction Safety**
   - Migration wrapped in `BEGIN`/`COMMIT` block
   - Proper error handling with `EXCEPTION` blocks
   - No DDL outside transactions (unless CONCURRENTLY)
   - Rollback points defined for long-running operations

3. **Idempotency**
   - Uses `IF NOT EXISTS` for CREATE statements
   - Uses `IF EXISTS` for DROP statements
   - `CREATE OR REPLACE` for functions/views
   - Safe re-execution on failure

4. **Performance Implications**
   - Index creation uses `CONCURRENTLY` for large tables
   - `ALTER TABLE` statements on large tables flagged for review
   - `VACUUM`, `ANALYZE` recommended after bulk updates
   - Proper use of batch operations for large data updates

5. **Security**
   - No hardcoded credentials or sensitive data
   - Proper permission grants (not `GRANT ALL`)
   - Role-based access control in place
   - `SECURITY DEFINER` functions justified and reviewed
   - Input validation in stored procedures

6. **Data Integrity**
   - Foreign key constraints validated
   - Check constraints include edge cases
   - Default values appropriate for data type
   - NOT NULL constraints have defaults for existing data

7. **Naming Conventions**
   - Table names follow project standards
   - Column names descriptive and consistent
   - Index names follow pattern: `idx_<table>_<column(s)>`
   - Constraint names follow pattern: `fk_<table>_<column>`, `chk_<table>_<column>`

8. **Documentation**
   - Header comments explain migration purpose
   - Work item ID referenced
   - Complex logic has inline comments
   - `COMMENT ON` statements for new schema objects

9. **Environment Safety**
   - Production scripts (`sqlcode/prod/`) have extra scrutiny
   - No `DROP DATABASE`, `DROP SCHEMA` in any script
   - `TRUNCATE` and `DELETE WITHOUT WHERE` flagged as high-risk
   - Schema name uses `app_env.connection_details.db_schema` reference (not hardcoded)

10. **Verification Block**
    - Every migration has post-execution verification
    - Verification uses `RAISE EXCEPTION` on failure
    - Checks that expected schema changes were applied

**Example review output**:
```
✅ PASS: Transaction safety (BEGIN/COMMIT present)
✅ PASS: Idempotency (IF NOT EXISTS used)
⚠️  WARNING: Large table ALTER detected (table: usage_data, est. rows: 5M)
   → Recommendation: Consider maintenance window
✅ PASS: Index uses CONCURRENTLY
⚠️  WARNING: No VACUUM ANALYZE after bulk update
   → Recommendation: Add VACUUM ANALYZE at end of script
✅ PASS: Verification block present
❌ FAIL: Schema name hardcoded as 'public' instead of using app_env.connection_details.db_schema
   → File: sqlcode/dev/migrations/20260719_add_column.sql, Line 23
```

#### B. Rollback Scripts Review

**File pattern**: `sqlcode/<env>/rollback/*_rollback.sql`

**Checks performed**:

1. **Completeness**
   - Every migration script has corresponding rollback script
   - Rollback operations reverse migration operations
   - Operations in reverse order of migration

2. **Safety**
   - Rollback wrapped in transaction
   - Verification block confirms rollback success
   - No data loss on rollback (unless explicitly documented)

3. **Idempotency**
   - Rollback can be re-run safely
   - Uses `IF EXISTS` for DROP operations

**Example review output**:
```
✅ PASS: Rollback script exists for migration
✅ PASS: Operations in reverse order
✅ PASS: Verification block present
⚠️  WARNING: Rollback will drop column with data
   → Recommendation: Document data loss in README
```

#### C. Stored Procedures/Functions Review

**File pattern**: `sqlcode/<env>/functions/*.sql`

**Checks performed**:

1. **Input Validation**
   - Parameters checked for NULL
   - Boundary conditions validated
   - Data type constraints enforced

2. **Error Handling**
   - `EXCEPTION` blocks for known error conditions
   - Meaningful error messages with context
   - No swallowed exceptions without logging

3. **Security**
   - `SECURITY DEFINER` vs `SECURITY INVOKER` appropriate
   - SQL injection prevention (no dynamic SQL with string concatenation)
   - Proper escaping if dynamic SQL used (`quote_ident`, `quote_literal`)

4. **Performance**
   - No N+1 query patterns
   - Proper use of indexes
   - Efficient JOIN strategies
   - Batch operations where appropriate

5. **Return Types**
   - Return type matches function signature
   - `RETURNS TABLE` used for multi-row returns
   - `RETURNS SETOF` appropriate

6. **Comments**
   - Function purpose documented
   - Parameters explained
   - Return value documented
   - `COMMENT ON FUNCTION` statement present

**Example review output**:
```
✅ PASS: Input validation present
✅ PASS: Error handling comprehensive
⚠️  WARNING: SECURITY DEFINER used
   → Recommendation: Justify elevated privileges in comments
❌ FAIL: Dynamic SQL vulnerable to injection
   → File: sqlcode/dev/functions/dynamic_query.sql, Line 45
   → Issue: EXECUTE 'SELECT * FROM ' || table_name (use quote_ident)
✅ PASS: Return type matches signature
```

#### D. Database Unit Tests Review

**File pattern**: `tests/test_db_*.py`

**Checks performed**:

1. **Test Coverage**
   - Every migration has corresponding test
   - Every stored procedure has test with sample data
   - Schema changes validated (columns, indexes, constraints)
   - Data integrity tests for foreign keys

2. **DBPool Usage**
   - Correct use of `await DBPool.get_pool()`
   - Proper `async with pool.acquire()` context manager
   - Transaction usage for data modifications
   - Connection cleanup (context manager auto-handles)

3. **Test Isolation**
   - Tests clean up test data after execution
   - No side effects between tests
   - Use of fixtures for setup/teardown

4. **Assertions**
   - Clear assertion messages
   - Tests for both success and failure cases
   - Edge cases covered (NULL, empty, boundary values)

5. **Schema References**
   - Uses `app_env.connection_details.db_schema` (not hardcoded)
   - Parameterized queries (`$1, $2, ...`)
   - No string interpolation for SQL

6. **Code Quality**
   - Follows `black` formatting (line-length 120)
   - Passes `flake8` linting
   - Proper async/await usage
   - Type hints where appropriate

**Example review output**:
```
✅ PASS: DBPool usage correct
✅ PASS: Test cleanup present
✅ PASS: Schema reference uses app_env
⚠️  WARNING: No test for NULL parameter case
   → Recommendation: Add test_stored_procedure_null_input
❌ FAIL: String interpolation used for SQL
   → File: tests/test_db_migration.py, Line 67
   → Issue: f"SELECT * FROM {table}" (use parameterized query)
✅ PASS: Black formatting
✅ PASS: Flake8 linting
```

### 3. Severity Levels

**❌ CRITICAL** (must fix before merge):
- SQL injection vulnerabilities
- Hardcoded credentials
- Missing rollback scripts
- Schema name hardcoded (not using `app_env`)
- Data loss without documentation
- DROP DATABASE/SCHEMA in scripts
- Transaction safety violations

**⚠️ HIGH** (should fix before merge):
- Missing verification blocks
- Poor error handling in stored procedures
- Large table operations without CONCURRENTLY
- Missing test coverage for critical paths
- Performance anti-patterns (N+1 queries)

**ℹ️ MEDIUM** (recommended to fix):
- Missing comments on complex logic
- Suboptimal index usage
- Missing VACUUM ANALYZE after bulk operations
- Test edge cases not covered

**✅ LOW** (nice to have):
- Additional inline comments
- Consistent naming improvements
- Refactoring opportunities

### 4. Generate Review Report

Create markdown report at `.claude/reviews/db-review-<timestamp>.md`:

```markdown
# Database Code Review Report

**Date**: <timestamp>  
**Reviewer**: Claude AI Auto-Reviewer  
**Environment**: <env>  
**Mode**: <normal | strict>

## Summary
- **Files reviewed**: <count>
- **Critical issues**: <count>
- **High issues**: <count>
- **Medium issues**: <count>
- **Low issues**: <count>

## Findings

### CRITICAL ❌
<list of critical issues with file:line references>

### HIGH ⚠️
<list of high issues with file:line references>

### MEDIUM ℹ️
<list of medium issues>

### LOW ✅
<list of low-priority suggestions>

## Files Reviewed
- [ ] `sqlcode/dev/migrations/20260719_add_column.sql` - ❌ 1 critical, ⚠️ 2 high
- [ ] `sqlcode/dev/rollback/20260719_add_column_rollback.sql` - ✅ Pass
- [ ] `sqlcode/dev/functions/calculate_usage.sql` - ⚠️ 1 high
- [ ] `tests/test_db_migration.py` - ❌ 1 critical

## Recommendations
1. Fix all CRITICAL issues before proceeding
2. Address HIGH issues before code review
3. Consider MEDIUM suggestions for code quality
4. LOW suggestions optional

## Next Steps
- [ ] Developer fixes critical issues
- [ ] Re-run auto-reviewer: `@auto-reviewer-db`
- [ ] Manual code review by senior developer (for prod scripts)
- [ ] Execute scripts in dev environment
- [ ] Run unit tests: `uv run pytest tests/test_db_*.py -v`
```

### 5. Exit Code

- **Exit 0**: No CRITICAL or HIGH issues found (or all resolved)
- **Exit 1**: CRITICAL issues found
- **Exit 2**: HIGH issues found (only in strict mode)

## Integration with Workflow

The auto-reviewer should be run:
1. **After script-writer-db completes** (before manual review)
2. **Before committing** (pre-commit hook integration)
3. **In CI/CD pipeline** (Azure DevOps pipeline)
4. **On-demand** by developers during development

## MCP Tools Used
- PostgreSQL MCP tools (for schema validation queries)
- Standard Claude Code tools: Read, Grep, Bash, Write (for report generation)

## Success Criteria
- [ ] All SQL files reviewed for syntax, security, performance
- [ ] All rollback scripts validated
- [ ] All stored procedures reviewed
- [ ] All unit tests reviewed
- [ ] Review report generated
- [ ] Critical issues flagged
- [ ] Recommendations provided

## Example Usage

```bash
# Review all uncommitted DB changes
@auto-reviewer-db

# Review specific migration script
@auto-reviewer-db --path sqlcode/dev/migrations/20260719_add_column.sql

# Review for production (strict mode)
@auto-reviewer-db --env prod --strict

# Review entire migrations directory
@auto-reviewer-db --path sqlcode/dev/migrations/
```

## Configuration

Review rules can be customized via `.claude/db/review-config.yml`:

```yaml
rules:
  sql_injection: CRITICAL
  hardcoded_schema: CRITICAL
  missing_rollback: CRITICAL
  large_table_alter: HIGH
  missing_verification: HIGH
  missing_comments: MEDIUM
  naming_conventions: LOW

performance:
  large_table_threshold: 1000000  # rows
  index_creation_concurrent: true

security:
  allowed_security_definer_functions:
    - "admin_only_function"
  
strict_mode:
  fail_on_warnings: true
  require_all_tests_pass: true
```

## Output Files
- **Review report**: `.claude/reviews/db-review-<timestamp>.md`
- **Issues JSON**: `.claude/reviews/db-review-<timestamp>.json` (for CI/CD integration)

## Safety Rules
- Never auto-fix CRITICAL issues without user approval
- Always show full context of issues (file, line, surrounding code)
- For production scripts, require manual senior developer review even if auto-review passes
- Flag any script that modifies data in production tables as HIGH risk
