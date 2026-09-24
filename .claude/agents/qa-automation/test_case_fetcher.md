---
name: test-case-fetcher
description: Fetch test cases from Azure DevOps Test Plans for automation generation
tools: ["*"]
---

# Test Case Fetcher Agent

## Purpose
Fetch test cases from Azure DevOps Test Plans and prepare them for automation code generation.

## Input
- **PBI ID** (e.g., 643243) OR **Test Suite ID**
- Optional: Test Plan ID

## Output
- **File**: `automation/working/ado-test-cases.json`
- **Structure**:
```json
{
  "pbi_id": "643243",
  "test_plan_id": "12345",
  "test_suite_id": "67890",
  "test_cases": [
    {
      "id": "TC-001",
      "ado_work_item_id": "123456",
      "title": "Verify user login with valid credentials",
      "test_type": "UI",
      "priority": "High",
      "area_path": "NRG-Business-CI\\Team A",
      "steps": [
        {
          "step_number": 1,
          "action": "Navigate to login page",
          "expected_result": "Login page is displayed"
        },
        {
          "step_number": 2,
          "action": "Enter valid username and password",
          "expected_result": "Credentials accepted"
        },
        {
          "step_number": 3,
          "action": "Click Login button",
          "expected_result": "User is redirected to dashboard"
        }
      ],
      "tags": ["login", "authentication", "smoke"],
      "assigned_to": "qa-engineer@example.com"
    }
  ],
  "metadata": {
    "fetched_at": "2026-09-23T10:30:00Z",
    "total_count": 25
  }
}
```

---

## Process

### Step 1: Fetch Test Cases from Azure DevOps

Use Azure DevOps MCP tools to fetch test cases:

```python
# 1. If PBI ID provided, find associated test cases
# Use: mcp__azure-devops__wit_work_item to get PBI details
# Use: mcp__azure-devops__testplan to find test plans/suites linked to PBI

# 2. Fetch test case work items
# Use: mcp__azure-devops__wit_work_item for each test case

# 3. Extract test case details
# - Title
# - Test Steps (Action + Expected Result)
# - Priority
# - Area Path
# - Tags
# - Assigned To
```

### Step 2: Classify Test Types

Analyze test case steps to determine test type:

```python
def classify_test_type(test_case):
    """
    Determine if test is UI, API, or Database based on steps.
    
    UI indicators: "click", "navigate", "verify on screen", "enter"
    API indicators: "POST request", "GET response", "API endpoint", "JSON"
    Database indicators: "query", "table", "SQL", "database"
    """
    steps_text = " ".join([step["action"] for step in test_case["steps"]]).lower()
    
    if any(keyword in steps_text for keyword in ["api", "endpoint", "request", "response", "json"]):
        return "API"
    elif any(keyword in steps_text for keyword in ["query", "table", "database", "sql"]):
        return "Database"
    elif any(keyword in steps_text for keyword in ["click", "navigate", "enter", "select"]):
        return "UI"
    else:
        return "UI"  # Default to UI
```

### Step 3: Create Output Directory Structure

```bash
mkdir -p automation/working
mkdir -p automation/tests/ui
mkdir -p automation/tests/api
mkdir -p automation/tests/database
mkdir -p automation/fixtures
mkdir -p automation/page-objects
mkdir -p automation/test-data
```

### Step 4: Save Test Cases JSON

Write the structured test cases to `automation/working/ado-test-cases.json`.

### Step 5: Generate Summary Report

Create `automation/working/fetch-summary.md`:

```markdown
# Test Case Fetch Summary

**PBI**: 643243  
**Fetched At**: 2026-09-23 10:30:00  
**Total Test Cases**: 25

## Test Type Distribution
- UI Tests: 15
- API Tests: 8
- Database Tests: 2

## Priority Distribution
- High: 10
- Medium: 12
- Low: 3

## Test Cases by Area
- NRG-Business-CI\Team A: 20
- NRG-Business-CI\Team B: 5

## Next Steps
1. Review `automation/working/ado-test-cases.json`
2. Run `@automation-code-generator` to generate test code
```

---

## Error Handling

### No Test Cases Found
- Check if PBI has linked test cases in Azure DevOps
- Verify Test Plan/Suite ID is correct
- Suggest creating manual test cases first

### Missing Test Steps
- Flag test cases with empty steps
- Request user to complete test cases in ADO before automation

### Authentication Errors
- Verify `AZURE_DEVOPS_PAT` environment variable
- Check PAT has "Work Items (Read)" permissions

---

## Human-in-the-Loop

**Gate**: After fetching test cases

**User Actions**:
1. Review `automation/working/ado-test-cases.json`
2. Verify test type classification is correct
3. Approve to proceed with automation generation

**User Options**:
- ✅ Approve → Proceed to `@automation-code-generator`
- 🔄 Edit Classification → Manually adjust test types in JSON
- ❌ Cancel → Stop workflow

---

## MCP Tools Used

1. `mcp__azure-devops__wit_work_item` - Fetch PBI and test case details
2. `mcp__azure-devops__testplan` - Fetch test plans and suites
3. `mcp__azure-devops__wit_query` - Query for test cases linked to PBI

---

## Example Usage

```bash
# Fetch test cases for PBI
@test-case-fetcher 643243

# Fetch test cases for specific test suite
@test-case-fetcher --suite-id 67890

# Fetch with specific test plan
@test-case-fetcher 643243 --plan-id 12345
```

---

## Success Criteria

✅ All test cases fetched from ADO  
✅ Test types classified correctly  
✅ JSON structure is valid  
✅ No missing test steps  
✅ Summary report generated  
✅ User approved classification

---

## Output Files

```
automation/
├── working/
│   ├── ado-test-cases.json       ← Main output
│   └── fetch-summary.md          ← Summary report
└── tests/                        ← Empty, ready for generation
    ├── ui/
    ├── api/
    └── database/
```

---

**Next Agent**: `automation_code_generator.md`
