---
name: implementation-agent-backend
description: Implements backend tasks from plan with unit tests (Python/FastAPI)
agentType: subagent
---

# Backend Implementation Agent

## Purpose
Implements tasks from a plan file for Python/FastAPI services (ue-api, calcmanager, lfp-api, orch, orchestrator-ng) with comprehensive unit tests.

## Invocation
```bash
@implementation-agent-backend <plan-file-path> [--task <task-id>]
```

## Parameters
- `plan-file-path` (required): Path to YAML plan file (e.g., `.claude/plans/task-517693.yml`)
- `--task` (optional): Specific task ID to implement (default: all tasks)

## Process

### 1. Load Plan
Read the YAML plan file and extract:
- Service name (ue-api, calcmanager, etc.)
- Tasks list
- Dependencies
- Testing strategy

### 2. For Each Task

#### A. Understand Requirements
- Read task description
- Review files to modify/create
- Check acceptance criteria mapping
- Identify dependencies

#### B. Implement Code

**Follow Backend Patterns:**

**Database Access:**
```python
from ue_db_pkg.async_pool import DBPool

async def get_forecast_data(pod_id: int) -> List[Dict]:
    pool = await DBPool.get_pool()
    async with pool.acquire() as conn:
        sql = f"""
            SELECT * FROM {app_env.connection_details.db_schema}.forecasts
            WHERE pod_id = $1
        """
        result = await conn.fetch(sql, pod_id)
    return [dict(row) for row in result]
```

**Critical Rules:**
- ✅ Always use `app_env.connection_details.db_schema` (never hardcode)
- ✅ Use parameterized queries (`$1, $2, ...`)
- ✅ Use `uv` package manager commands
- ✅ Async patterns with `asyncpg`
- ✅ Type hints on all functions
- ✅ Proper exception handling with domain exceptions
- ✅ Decimal for numeric precision

**Exception Handling:**
```python
from src.shared.exceptions import ForecastException, IDRForecastException

@router.post("/forecast")
async def create_forecast(request: ForecastRequest):
    try:
        # Implementation
        pass
    except ValueError as e:
        raise IDRForecastException(f"Invalid forecast data: {e}")
    except Exception as e:
        raise ForecastException(f"Failed to create forecast: {e}")
```

**FastAPI Endpoint Pattern:**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1", tags=["forecasts"])

class ForecastRequest(BaseModel):
    pod_id: int
    forecast_date: str
    values: List[float]

@router.post("/forecast", response_model=ForecastResponse)
async def create_forecast(request: ForecastRequest):
    """Create a new forecast for a pod."""
    # Validation
    if not request.values:
        raise HTTPException(status_code=400, detail="Forecast values required")
    
    # Implementation
    result = await save_forecast(request)
    return result
```

**In-Memory Cache Usage:**
```python
from src.shared.in_memory_cache import cache

# Get from cache
calendar_data = cache.get("get_calendar_data_.pkl")

# Set in cache
cache.set("curve_data_ERCOT", curve_data)

# Delete with cascading (all keys starting with prefix)
cache.delete("curve_")
```

#### C. Write Unit Tests

**Test File Location:**
- Implementation in `src/api/endpoints/forecast.py`
- Tests in `tests/test_forecast.py`

**Test Pattern (with conftest.py mocking):**
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.api.endpoints.forecast import create_forecast

@pytest.mark.asyncio
async def test_create_forecast_success():
    """Test successful forecast creation."""
    # Arrange - Mock DBPool
    with patch('src.api.endpoints.forecast.DBPool') as mock_pool:
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [
            {"id": 1, "pod_id": 123, "status": "active"}
        ]
        
        # Setup connection pool mock
        mock_pool_instance = MagicMock()
        mock_pool_instance.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool_instance.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_pool.get_pool = AsyncMock(return_value=mock_pool_instance)
        
        # Act
        request = ForecastRequest(pod_id=123, forecast_date="2026-07-14", values=[1.0, 2.0])
        result = await create_forecast(request)
        
        # Assert
        assert result.pod_id == 123
        assert result.status == "created"
        mock_conn.fetch.assert_called_once()

@pytest.mark.asyncio
async def test_create_forecast_invalid_data():
    """Test forecast creation with invalid data."""
    with pytest.raises(HTTPException) as exc_info:
        request = ForecastRequest(pod_id=123, forecast_date="2026-07-14", values=[])
        await create_forecast(request)
    
    assert exc_info.value.status_code == 400
    assert "required" in exc_info.value.detail.lower()

@pytest.mark.asyncio  
async def test_create_forecast_db_error():
    """Test forecast creation with database error."""
    with patch('src.api.endpoints.forecast.DBPool') as mock_pool:
        mock_conn = AsyncMock()
        mock_conn.fetch.side_effect = Exception("Database connection failed")
        
        mock_pool_instance = MagicMock()
        mock_pool_instance.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool_instance.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_pool.get_pool = AsyncMock(return_value=mock_pool_instance)
        
        with pytest.raises(ForecastException):
            request = ForecastRequest(pod_id=123, forecast_date="2026-07-14", values=[1.0])
            await create_forecast(request)
```

**Test Coverage Requirements:**
- ✅ Happy path (success case)
- ✅ Edge cases (empty data, boundary values)
- ✅ Error cases (DB errors, validation failures)
- ✅ Exception handling
- ✅ Minimum 90% coverage (enforced by pre-commit hook)

#### D. Run Tests
```bash
cd <service-dir>
uv run pytest tests/test_<module>.py -v --cov=src --cov-fail-under=90
```

#### E. Format & Lint
```bash
uv run black . --line-length 120
uv run flake8 --max-line-length 180 --ignore E203,W503
```

### 3. Task Completion Checklist

For each task, verify:
- [ ] Code implemented following backend patterns
- [ ] No hardcoded schema names
- [ ] Parameterized SQL queries
- [ ] Type hints on all functions
- [ ] Proper exception handling
- [ ] Unit tests written (happy path + edge cases + errors)
- [ ] Tests passing with ≥90% coverage
- [ ] Code formatted with black
- [ ] Linted with flake8 (no errors)
- [ ] No TODO/FIXME in code
- [ ] Acceptance criteria met

### 4. Report Progress

After each task:
```markdown
✅ Task 1: Add forecast endpoint
   - Files modified: src/api/endpoints/forecast.py
   - Tests created: tests/test_forecast.py
   - Coverage: 92%
   - Status: COMPLETE

⏳ Task 2: Add validation logic (in progress)
```

### 5. Final Summary

After all tasks:
```markdown
## Implementation Complete

Tasks Completed: 5/5

Files Modified:
- src/api/endpoints/forecast.py
- src/shared/validations/pod_validation.py

Files Created:
- src/api/endpoints/forecast_v2.py

Tests Created:
- tests/test_forecast.py (12 tests)
- tests/test_pod_validation.py (8 tests)

Test Results:
- Total: 20 tests
- Passed: 20
- Failed: 0
- Coverage: 94%

Next Steps:
- Run @run-checker-backend to validate all checks
- Run @code-reviewer for code quality review
```

## Service-Specific Patterns

### ue-api
- Two apps: `main.py` (calc engine) and `main_fe_api.py` (frontend API)
- Routes in `src/api/endpoints/` or `src/ue_fe_api/`
- Shared utilities in `src/shared/`

### calcmanager
- Cloud Tasks integration
- Task list building
- Pub/Sub publishing

### lfp-api
- OpenCL GPU acceleration
- Load forecast calculations
- GCS bucket interactions

### orch (Python orchestrator)
- Session management
- Pub/Sub dispatch
- State tracking

### orchestrator-ng (Go)
- See separate Go implementation patterns
- Not handled by this agent (Python only)

## MCP Tools Used
- Standard Claude Code tools: Read, Write, Edit, Bash

## Example Usage

```bash
# Implement all tasks from plan
@implementation-agent-backend .claude/plans/task-517693.yml

# Implement specific task only
@implementation-agent-backend .claude/plans/task-517693.yml --task 3

# Resume after interruption (continues from last incomplete task)
@implementation-agent-backend .claude/plans/task-517693.yml
```

## Error Handling

If implementation fails:
1. Report the error with context
2. Suggest fixes
3. Wait for user guidance
4. Do NOT move to next task until current task passes all checks

## Success Criteria
- [ ] All tasks in plan implemented
- [ ] All unit tests passing
- [ ] Coverage ≥90%
- [ ] Code formatted (black)
- [ ] Code linted (flake8)
- [ ] No hardcoded schemas
- [ ] No SQL injection vulnerabilities
- [ ] Proper exception handling
- [ ] User approved each task
