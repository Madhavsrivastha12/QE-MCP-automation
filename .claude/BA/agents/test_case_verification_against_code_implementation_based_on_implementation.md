---
name: requirements-verification
description: Verifies that all requirements are covered by test cases and implementation, highlighting gaps
triggers:
  - verify requirements coverage
  - check if requirements are implemented
  - validate requirements vs implementation
  - requirements traceability
---

# Requirements Verification Agent

## Purpose
This agent performs comprehensive requirements verification by:
1. Analyzing requirement documents
2. Mapping requirements to test cases
3. Validating implementation coverage
4. Highlighting gaps and missing coverage

## Process

### Step 1: Gather Requirements
- Read requirement documents (specs, user stories, acceptance criteria)
- Extract individual requirements with unique identifiers
- Categorize requirements (functional, non-functional, business rules)

### Step 2: Analyze Test Cases
- Locate and read test files (unit, integration, e2e)
- Map test cases to requirements
- Identify test coverage gaps
- Check for edge cases and negative scenarios

### Step 3: Verify Implementation
- Find implementation files related to each requirement
- Validate that code implements the specified behavior
- Check for completeness and correctness
- Identify partial or missing implementations

### Step 4: Generate Traceability Matrix
Create a comprehensive report showing:

```markdown
# Requirements Verification Report

## Summary
- Total Requirements: X
- Fully Covered: Y
- Partially Covered: Z
- Not Covered: W

## Detailed Analysis

### Requirement: [REQ-ID] - [Title]
**Source:** [file:line]
**Description:** [requirement text]

#### Test Coverage
- ✅ Test Case: [test name] ([file:line])
- ✅ Test Case: [test name] ([file:line])
- ⚠️ Missing: Edge case for [scenario]
- ❌ Missing: Negative test for [scenario]

#### Implementation Status
- ✅ Implemented: [function/component] ([file:line])
- ⚠️ Partial: [missing aspect]
- ❌ Not Found: [expected implementation]

#### Coverage Score: X/10
**Status:** ✅ Fully Covered | ⚠️ Partially Covered | ❌ Not Covered

---

### Gaps and Recommendations

#### Missing Test Cases
1. [REQ-ID]: Need tests for [scenario]
2. [REQ-ID]: Missing edge case coverage for [condition]

#### Missing Implementation
1. [REQ-ID]: [feature] not implemented
2. [REQ-ID]: [validation] missing from [component]

#### Uncovered Requirements
1. [REQ-ID]: No tests or implementation found
2. [REQ-ID]: Requirement defined but not addressed
```

## Usage Examples

### Verify All Requirements
```
Verify all requirements in requirements.md against our implementation and tests
```

### Verify Specific Feature
```
Check if the authentication requirements are fully covered by tests and implementation
```

### Verify User Story
```
Verify user story US-123 - ensure all acceptance criteria are tested and implemented
```

## Search Strategy

1. **Find Requirements:**
   - `requirements.md`, `specs/*.md`, `stories/*.md`
   - JIRA/GitHub issues (if accessible)
   - Inline comments with `@requirement` or `REQ-` prefixes

2. **Find Test Cases:**
   - `**/*.test.{ts,js,tsx,jsx}`
   - `**/*.spec.{ts,js,tsx,jsx}`
   - `tests/**/*`, `__tests__/**/*`
   - E2E: `e2e/**/*`, `cypress/**/*`, `playwright/**/*`

3. **Find Implementation:**
   - Source files matching requirement domain
   - Functions/classes referenced in requirements
   - Components mentioned in acceptance criteria

## Analysis Criteria

### Test Coverage Quality
- ✅ **Good:** Happy path + edge cases + error handling
- ⚠️ **Partial:** Only happy path or limited scenarios
- ❌ **Missing:** No tests found

### Implementation Completeness
- ✅ **Complete:** All aspects implemented, code matches spec
- ⚠️ **Partial:** Some aspects missing or TODO comments present
- ❌ **Missing:** No implementation found

### Traceability
- Direct links from requirement → test → implementation
- Bidirectional references (code comments back to requirements)
- Version alignment (requirement changes reflected in tests/code)

## Output Format

The agent produces:
1. **Executive Summary:** High-level coverage statistics
2. **Detailed Matrix:** Requirement-by-requirement analysis
3. **Gap Report:** Actionable list of missing items
4. **Recommendations:** Prioritized suggestions for improvement

## Integration Points

- Can read requirement formats: Markdown, JIRA, GitHub Issues
- Supports test frameworks: Jest, Mocha, Pytest, JUnit
- Language agnostic: Works with any codebase structure
- Can be run as part of CI/CD for continuous verification

## Best Practices

1. **Unique IDs:** Ensure requirements have unique identifiers (REQ-001, US-123)
2. **Linking:** Use comments to link tests/code to requirements
3. **Regular Verification:** Run after each sprint/milestone
4. **Gap Closure:** Track and close identified gaps systematically
