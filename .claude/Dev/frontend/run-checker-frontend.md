---
name: run-checker-frontend
description: Runs all quality checks for React/TypeScript frontend (tests, lint, type checks, coverage)
agentType: subagent
---

# Frontend Run Checker Agent

## Purpose
Executes all quality checks for the React/TypeScript frontend (ue-frontend): tests, linting, formatting, type checking, and coverage validation.

## Invocation
```bash
@run-checker-frontend [--skip-tests] [--skip-lint] [--skip-format] [--skip-types]
```

## Parameters
- `--skip-tests` (optional): Skip test execution
- `--skip-lint` (optional): Skip linting
- `--skip-format` (optional): Skip format checking
- `--skip-types` (optional): Skip type checking

## Process

### 1. Navigate to Frontend Directory
```bash
cd ue-frontend
```

### 2. Run Checks

Execute checks in this order (fail fast on first failure):

#### Check 1: Type Check (TypeScript)
```bash
npm run type-check
# Or directly: npx tsc --noEmit
```

**Expected**: No type errors

**If fails**:
```
❌ Type Check: FAILED

src/components/ForecastDashboard/ForecastDashboard.tsx:42:7
  Type 'string | undefined' is not assignable to type 'string'
  
src/hooks/useForecastData.ts:23:12
  Property 'data' does not exist on type 'never'

Total errors: 2
```

#### Check 2: Lint Check (ESLint)
```bash
npm run lint
```

**Expected**: No linting errors or warnings

**If fails**:
```
❌ Lint Check: FAILED

/src/components/ForecastDashboard.tsx
  42:7   error    'data' is assigned but never used          @typescript-eslint/no-unused-vars
  67:23  warning  Missing key prop for element in iterator   react/jsx-key
  89:5   error    Fast refresh only works when a file only exports components  react-refresh/only-export-components

/src/hooks/useForecastData.ts
  15:1   error    React Hook useCallback has a missing dependency: 'queryClient'  react-hooks/exhaustive-deps

✖ 4 problems (3 errors, 1 warning)
```

#### Check 3: Format Check (Prettier)
```bash
npx prettier --check "src/**/*.{ts,tsx,js,jsx,json,css}"
```

**Expected**: All files formatted correctly

**If fails**:
```
❌ Format Check: FAILED

Checking formatting...
src/components/ForecastDashboard/ForecastDashboard.tsx
src/hooks/useForecastData.ts
src/types/forecast.ts

Code style issues found in 3 files.
Run 'npm run format' to fix.
```

#### Check 4: Import Check
```bash
npm run build:dev 2>&1 | head -20
```

**Expected**: Build succeeds (validates all imports)

**If fails**:
```
❌ Import Check: FAILED

ERROR in ./src/components/ForecastDashboard.tsx
Module not found: Error: Can't resolve '@/components/LoadingSpinner'

ERROR in ./src/hooks/useForecastData.ts
Module not found: Error: Can't resolve '@/api/forecast'
```

#### Check 5: Unit Tests
```bash
npm test -- --coverage --watchAll=false
```

**Expected**: 
- All tests pass
- Coverage ≥70%

**Coverage thresholds** (from jest.config.js):
```json
{
  "coverageThreshold": {
    "global": {
      "statements": 70,
      "branches": 70,
      "functions": 70,
      "lines": 70
    }
  }
}
```

**If fails**:
```
❌ Unit Tests: FAILED

Test Suites: 2 failed, 8 passed, 10 total
Tests:       3 failed, 2 skipped, 45 passed, 50 total

Failed Tests:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ForecastDashboard › handles create forecast action
   
   Expected: "createForecast" to have been called
   Received: 0 calls
   
   at src/components/ForecastDashboard/__tests__/ForecastDashboard.test.tsx:87:12

2. useForecastData › invalidates cache on create
   
   TypeError: Cannot read property 'invalidateQueries' of undefined
   
   at src/hooks/__tests__/useForecastData.test.ts:45:23

3. ForecastChart › renders chart with data
   
   ReferenceError: ResizeObserver is not defined
   
   at node_modules/recharts/...

Coverage Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
File                    | % Stmts | % Branch | % Funcs | % Lines | Uncovered Lines
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All files              |   65.23 |    58.12 |   62.45 |   64.89 |
 ForecastDashboard.tsx |   54.12 |    45.00 |   50.00 |   53.78 | 42-45, 67-89, 123-145
 useForecastData.ts    |   71.23 |    65.00 |   70.00 |   70.56 | 23-28, 45-52
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Coverage threshold not met:
   Global statements: 65.23% < 70%
   Global branches: 58.12% < 70%
```

#### Check 6: Test File Existence
Verify that for each component/hook, corresponding test file exists:

```
src/components/ForecastDashboard/ForecastDashboard.tsx
  → __tests__/ForecastDashboard.test.tsx ✅

src/hooks/useForecastData.ts
  → __tests__/useForecastData.test.ts ✅

src/components/NewComponent/NewComponent.tsx
  → __tests__/NewComponent.test.tsx ❌ MISSING
```

**If missing**:
```
⚠️  Test Coverage Warning:
Missing test files:
- src/components/NewComponent/__tests__/NewComponent.test.tsx
```

#### Check 7: Route Generation
```bash
npm run generate:routes
git diff --exit-code src/routeTree.gen.ts
```

**Expected**: Route tree is up-to-date

**If fails**:
```
⚠️  Routes Warning:
Route tree is out of sync. Run 'npm run generate:routes' and commit the changes.
```

### 3. Generate Report

#### Success Report
```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ALL CHECKS PASSED - ue-frontend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Type Check       TypeScript (strict mode)
✅ Lint Check       ESLint (no errors, no warnings)
✅ Format Check     Prettier (all files formatted)
✅ Import Check     Vite build successful
✅ Unit Tests       50 passed, 0 failed
✅ Coverage         76% (threshold: 70%)
✅ Test Files       All components/hooks have tests
✅ Routes           Route tree up-to-date

Test Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test Suites:     10 passed, 10 total
Tests:           50 passed, 50 total
Duration:        8.5s

Coverage:
  Statements:    76.23%
  Branches:      74.56%
  Functions:     78.12%
  Lines:         75.89%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommendation: ✅ READY TO MERGE
```

#### Failure Report
```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ CHECKS FAILED - ue-frontend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Type Check       TypeScript (strict mode)
❌ Lint Check       4 problems (3 errors, 1 warning)
❌ Format Check     3 files need formatting
✅ Import Check     Vite build successful
❌ Unit Tests       3 failed, 45 passed
❌ Coverage         65% (below 70% threshold)
⚠️  Test Files       1 missing test file
⚠️  Routes           Route tree out of sync

Failed Checks Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Lint Check:
  src/components/ForecastDashboard.tsx
    42:7   error    'data' is assigned but never used
    67:23  warning  Missing key prop for element in iterator
  
  src/hooks/useForecastData.ts
    15:1   error    React Hook useCallback has missing dependency: 'queryClient'
  
  Fix: npm run lint:fix

Format Check:
  Files need formatting:
  - src/components/ForecastDashboard/ForecastDashboard.tsx
  - src/hooks/useForecastData.ts
  - src/types/forecast.ts
  
  Fix: npm run format

Unit Tests:
  Failed tests:
  1. ForecastDashboard › handles create forecast action
  2. useForecastData › invalidates cache on create
  3. ForecastChart › renders chart with data (ResizeObserver not defined)

Coverage:
  Current: 65.23%
  Required: 70%
  Missing coverage in:
  - ForecastDashboard.tsx lines 42-45, 67-89, 123-145
  - useForecastData.ts lines 23-28, 45-52

Test Files:
  Missing:
  - src/components/NewComponent/__tests__/NewComponent.test.tsx

Routes:
  Run: npm run generate:routes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recommendation: ❌ DO NOT MERGE
Fix all failed checks before proceeding.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. Exit Code

Return appropriate exit code:
- `0`: All checks passed
- `1`: Format/lint failures only
- `2`: Type errors
- `3`: Test failures
- `4`: Coverage below threshold
- `5`: Multiple check failures

## Auto-Fix Mode

If user approves, can auto-fix some issues:

```bash
@run-checker-frontend --auto-fix
```

Auto-fixes:
1. **Lint issues**: Run `npm run lint:fix`
2. **Format issues**: Run `npm run format`
3. **Route tree**: Run `npm run generate:routes`

Does NOT auto-fix:
- Type errors (requires code changes)
- Test failures (requires debugging)
- Coverage gaps (requires writing tests)

## Common Test Setup Issues

### ResizeObserver Mock
```typescript
// jest.setup.ts
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));
```

### IntersectionObserver Mock
```typescript
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));
```

### Window.matchMedia Mock
```typescript
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});
```

## Integration with Workflow

Called by:
- `@frontend-workflow` (after implementation, before code review)
- Can be run standalone anytime

## Husky Pre-commit Hook Simulation

This agent simulates what the husky pre-commit hook will check:
- Type checking (tsc)
- Linting (eslint)
- Tests passing
- Coverage ≥70%

If this passes, husky hook should also pass.

## MCP Tools Used
None (uses standard Claude Code tools: Bash)

## Example Usage

```bash
# Run all checks
@run-checker-frontend

# Skip tests (type/lint/format only)
@run-checker-frontend --skip-tests

# Auto-fix lint and format issues
@run-checker-frontend --auto-fix

# Skip type checking (fast check)
@run-checker-frontend --skip-types
```

## Success Criteria
- [ ] All checks executed in order
- [ ] Clear pass/fail status for each check
- [ ] Detailed error messages for failures
- [ ] Actionable fix suggestions
- [ ] Coverage report with uncovered lines
- [ ] Test summary with counts
- [ ] Merge recommendation provided
- [ ] Exit code reflects overall status
