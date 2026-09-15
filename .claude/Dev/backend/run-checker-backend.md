---
name: run-checker-backend
description: Runs all quality checks for Python/FastAPI services (tests, lint, type checks, coverage)
agentType: subagent
---

# Backend Run Checker Agent

## Purpose
Executes all quality checks for Python/FastAPI backend services: tests, linting, formatting, type checking, and coverage validation.

## Invocation
```bash
@run-checker-backend [<service-path>] [--skip-tests] [--skip-lint] [--skip-format]
```

## Parameters
- `service-path` (optional): Service directory to check (e.g., `ue-api`, `calcmanager`). Default: auto-detect from current directory
- `--skip-tests` (optional): Skip test execution
- `--skip-lint` (optional): Skip linting
- `--skip-format` (optional): Skip format checking

## Process

### 1. Detect Service

If `service-path` not provided, detect from:
- Current working directory
- Git branch name (extract service from `task-<id>-<service>-<desc>`)
- Modified files in git diff

Supported services:
- `ue-api`
- `calcmanager`
- `lfp-api`
- `orch`
- `batch-load-job`

### 2. Run Checks

Execute checks in this order (fail fast on first failure):

#### Check 1: Format Check (Black)
```bash
cd <service-path>
uv run black . --check --line-length 120
```

**Expected**: All files formatted correctly

**If fails**:
```
❌ Format Check: FAILED
Files need formatting:
- src/api/endpoints/forecast.py
- src/shared/validations/pod_validation.py

Run to fix:
  uv run black . --line-length 120
```

#### Check 2: Lint Check (Flake8)
```bash
cd <service-path>
uv run flake8 --max-line-length 180 --ignore E203,W503
```

**Expected**: No linting errors

**If fails**:
```
❌ Lint Check: FAILED
src/api/endpoints/forecast.py:42:80: E501 line too long (185 > 180 characters)
src/shared/utils.py:15:1: F401 'typing.Dict' imported but unused

Total errors: 2
```

#### Check 3: Type Check (MyPy - if configured)
```bash
cd <service-path>
uv run mypy src/ --ignore-missing-imports 2>/dev/null || echo "MyPy not configured, skipping"
```

**Expected**: No type errors (or skipped if not configured)

**If fails**:
```
❌ Type Check: FAILED
src/api/endpoints/forecast.py:42: error: Incompatible return type
```

#### Check 4: Import Check
```bash
cd <service-path>
uv run python -c "import sys; sys.path.insert(0, 'src'); import api.endpoints.forecast" 2>&1
```

**Expected**: All imports successful

**If fails**:
```
❌ Import Check: FAILED
ModuleNotFoundError: No module named 'xyz'
```

#### Check 5: Unit Tests
```bash
cd <service-path>
uv run pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=90
```

**Expected**: 
- All tests pass
- Coverage ≥90%

**If fails**:
```
❌ Unit Tests: FAILED

Test Results:
- Total: 25
- Passed: 23
- Failed: 2
- Errors: 0

Failed Tests:
1. tests/test_forecast.py::test_create_forecast_invalid_data
   AssertionError: Expected status_code 400, got 500

2. tests/test_pod_validation.py::test_validate_pod_not_found
   KeyError: 'pod_id'

Coverage: 87% (below 90% threshold)
Missing coverage in:
- src/api/endpoints/forecast.py lines 42-45, 67-72
```

#### Check 6: Test File Existence
Verify that for each modified source file, corresponding test file exists:

```python
src/api/endpoints/forecast.py → tests/test_forecast.py ✅
src/shared/validations/pod.py → tests/test_pod_validation.py ❌ MISSING
```

**If missing**:
```
⚠️  Test Coverage Warning:
Missing test files:
- tests/test_pod_validation.py (for src/shared/validations/pod.py)
```

### 3. Generate Report

#### Success Report
```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ALL CHECKS PASSED - ue-api
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Format Check      black (line-length 120)
✅ Lint Check        flake8 (max 180, ignore E203,W503)
✅ Type Check        mypy (skipped - not configured)
✅ Import Check      All modules importable
✅ Unit Tests        25 passed, 0 failed
✅ Coverage          94% (threshold: 90%)
✅ Test Files        All source files have tests

Test Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Tests:     25
Passed:          25
Failed:          0
Skipped:         0
Duration:        12.3s
Coverage:        94%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommendation: ✅ READY TO MERGE
```

#### Failure Report
```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ CHECKS FAILED - ue-api
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Format Check      2 files need formatting
✅ Lint Check        flake8 (max 180, ignore E203,W503)
⏭️  Type Check        mypy (skipped - not configured)
✅ Import Check      All modules importable
❌ Unit Tests        2 failed, 23 passed
❌ Coverage          87% (below 90% threshold)
⚠️  Test Files        1 missing test file

Failed Checks Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Format Check:
  Files need formatting:
  - src/api/endpoints/forecast.py
  - src/shared/validations/pod_validation.py
  
  Fix: uv run black . --line-length 120

Unit Tests:
  Failed tests:
  1. tests/test_forecast.py::test_create_forecast_invalid_data
     AssertionError: Expected status_code 400, got 500
  
  2. tests/test_pod_validation.py::test_validate_pod_not_found
     KeyError: 'pod_id'

Coverage:
  Current: 87%
  Required: 90%
  Missing coverage:
  - src/api/endpoints/forecast.py lines 42-45, 67-72

Test Files:
  Missing:
  - tests/test_pod_validation.py (for src/shared/validations/pod.py)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recommendation: ❌ DO NOT MERGE
Fix all failed checks before proceeding.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. Exit Code

Return appropriate exit code:
- `0`: All checks passed
- `1`: Format/lint failures only
- `2`: Test failures
- `3`: Coverage below threshold
- `4`: Multiple check failures

## Service-Specific Configurations

### ue-api
```bash
# Two apps: main.py (calc engine) and main_fe_api.py (frontend API)
# Coverage omits src/ue_fe_api/* (see .coveragerc)
uv run pytest tests/ --cov=src --cov-fail-under=90
```

### calcmanager / lfp-api / orch
```bash
# Standard configuration
uv run pytest tests/ --cov=src --cov-fail-under=90
```

### batch-load-job
```bash
# Cloud Run job - may have different test setup
uv run pytest tests/ --cov=src --cov-fail-under=80  # Lower threshold if needed
```

## Auto-Fix Mode

If user approves, can auto-fix some issues:

```bash
@run-checker-backend --auto-fix
```

Auto-fixes:
1. **Format issues**: Run `uv run black . --line-length 120`
2. **Import sorting**: Run `uv run isort .` (if configured)

Does NOT auto-fix:
- Lint errors (requires manual code changes)
- Test failures (requires debugging)
- Coverage gaps (requires writing tests)

## Integration with Workflow

Called by:
- `@backend-workflow` (after implementation, before code review)
- Can be run standalone anytime

## Pre-commit Hook Simulation

This agent simulates what the pre-commit hook will check:
- Branch naming: `task-<ticket>-<desc>` or `bug-<ticket>-<desc>`
- Coverage: ≥90%
- Tests passing

If this passes, pre-commit hook should also pass.

## MCP Tools Used
None (uses standard Claude Code tools: Bash)

## Example Usage

```bash
# Auto-detect service from current directory
@run-checker-backend

# Explicit service
@run-checker-backend ue-api

# Skip tests (format/lint only)
@run-checker-backend ue-api --skip-tests

# Auto-fix format issues
@run-checker-backend --auto-fix
```

## Success Criteria
- [ ] All checks executed in order
- [ ] Clear pass/fail status for each check
- [ ] Detailed error messages for failures
- [ ] Actionable fix suggestions
- [ ] Coverage report with missing lines
- [ ] Test summary with counts
- [ ] Merge recommendation provided
- [ ] Exit code reflects overall status
