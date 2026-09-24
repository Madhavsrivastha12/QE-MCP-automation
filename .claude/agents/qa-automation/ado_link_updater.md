---
name: ado-link-updater
description: Update Azure DevOps test cases with automation links (PR + test file paths)
tools: ["*"]
---

# ADO Link Updater Agent

## Purpose
Update Azure DevOps test cases with links to automation code (PR URL and test file paths), and set automation status field.

## Input
- `automation/working/test-mapping.json` (ADO ID → Test file mapping)
- PR URL
- PBI metadata

## Output
- ADO test cases updated with:
  - Automation Status = "Automated"
  - PR link in description
  - Test file path in description
- Update summary report: `automation/working/ado-update-summary.md`

---

## Process

### Step 1: Read Test Mapping

Load `automation/working/test-mapping.json`:
```json
{
  "mappings": [
    {
      "ado_work_item_id": "123456",
      "test_case_id": "TC-001",
      "test_file": "automation/tests/ui/login.spec.ts",
      "test_type": "UI",
      "test_name": "should login successfully with valid credentials"
    }
  ]
}
```

### Step 2: Read PR Details

Extract from `automation/working/pr-summary.md`:
- PR URL
- PR ID
- Branch name

### Step 3: Update Each Test Case in ADO

For each test case in mapping, update the Azure DevOps work item:

**Update Fields**:
1. **Automation Status** = "Automated"
2. **Description** (append to existing):

```markdown
---

## 🤖 Automation Details

**Status**: Automated ✅

**Test File**: `{TEST_FILE_PATH}`

**Test Name**: `{TEST_NAME}`

**Framework**: {FRAMEWORK} ({UI: Playwright, API/DB: Pytest})

**Pull Request**: [{PR_TITLE}]({PR_URL})

**Branch**: `{BRANCH_NAME}`

**Automated Date**: {CURRENT_DATE}

**How to Run**:
```bash
# UI Test (Playwright)
npx playwright test {TEST_FILE_NAME}

# API/DB Test (Pytest)
pytest {TEST_FILE_PATH} -v
```

**Repository Path**: `{REPO_PATH}/{TEST_FILE_PATH}`

---
```

**MCP Tool Call**:
```python
# Update test case work item
mcp__azure_devops__wit_work_item_write(
    work_item_id=ado_work_item_id,
    fields={
        "System.Description": updated_description,
        "Microsoft.VSTS.TCM.AutomationStatus": "Automated",
        "System.Tags": existing_tags + "; Automated"
    }
)
```

### Step 4: Add Comment to Test Case

Add a comment to the test case tracking automation:

**Comment Template**:
```markdown
## Automation Test Added

This test case has been automated and is now available in the repository.

**PR**: [{PR_TITLE}]({PR_URL})

**Test File**: `{TEST_FILE_PATH}`

**Test Type**: {TEST_TYPE}

**How to Run Locally**:
```bash
{RUN_COMMAND}
```

**CI/CD**: This test will run automatically on every PR and merge to main.

**Status**: ✅ Automated
```

**MCP Tool Call**:
```python
# Add comment to work item
mcp__azure_devops__wit_work_item_comment_write(
    work_item_id=ado_work_item_id,
    comment_text=comment_text
)
```

### Step 5: Link Test Case to PR

Create a link between the test case and the pull request:

**MCP Tool Call**:
```python
# Link test case to PR
mcp__azure_devops__wit_work_item_link_write(
    work_item_id=ado_work_item_id,
    link_type="Related",
    target_id=pr_id,
    comment="Automation test created in this PR"
)
```

### Step 6: Update PBI Description

Update the original PBI with automation summary:

**Append to PBI Description**:
```markdown
---

## 🤖 Automation Test Coverage

**Total Test Cases Automated**: {TOTAL_COUNT}

**Automation PR**: [{PR_TITLE}]({PR_URL})

**Test Breakdown**:
- UI Tests (Playwright): {UI_COUNT}
- API Tests (Pytest): {API_COUNT}
- Database Tests (Pytest): {DB_COUNT}

**Repository Location**: `automation/tests/`

**Automated Test Cases**:
{LIST_OF_TEST_CASE_LINKS}

**How to Run All Tests**:
```bash
# UI Tests
npx playwright test

# API/Database Tests
pytest automation/tests/ -v
```

**CI/CD Status**: ✅ Tests running in pipeline

**Automation Date**: {CURRENT_DATE}

---
```

### Step 7: Generate Update Summary Report

Create `automation/working/ado-update-summary.md`:

```markdown
# ADO Update Summary

**Updated Date**: {CURRENT_DATE}

**PR URL**: {PR_URL}

**PBI**: #{PBI_ID}

---

## Test Cases Updated

| ADO ID | Test Case Title | Test File | Type | Status |
|--------|----------------|-----------|------|--------|
| #123456 | Verify user login | login.spec.ts | UI | ✅ Updated |
| #123457 | Verify user API | test_user_api.py | API | ✅ Updated |
| #123458 | Verify DB schema | test_user_schema.py | DB | ✅ Updated |
| ... | ... | ... | ... | ... |

**Total Updated**: {TOTAL_COUNT} test cases

---

## Updates Applied

For each test case:
- ✅ Automation Status set to "Automated"
- ✅ PR link added to description
- ✅ Test file path added to description
- ✅ Comment added with run instructions
- ✅ Linked to PR work item
- ✅ Tag "Automated" added

---

## PBI Updated

**PBI #{PBI_ID}** updated with:
- ✅ Automation summary added to description
- ✅ Test coverage breakdown
- ✅ Links to all automated test cases

---

## Verification Steps

To verify updates:
1. Open PBI #{PBI_ID} in Azure DevOps
2. Check "Automation Test Coverage" section in description
3. Open each test case and verify:
   - Automation Status = "Automated"
   - "Automation Details" section in description
   - Comment with run instructions
   - Link to PR

---

## Next Steps

1. ✅ Merge PR after code review approval
2. ⏳ Run automation tests in CI/CD
3. ⏳ Monitor test execution results
4. ⏳ Update test cases if any failures

---

## Rollback Instructions

If updates need to be reverted:
```bash
# Revert test case automation status
# (Manual process - update each test case in ADO UI)
```

---

## Automation Coverage Report

**Total Test Cases in PBI**: {TOTAL_TC_COUNT}  
**Automated**: {AUTOMATED_COUNT}  
**Manual**: {MANUAL_COUNT}  
**Coverage**: {COVERAGE_PERCENTAGE}%

```
███████████████░░░░░ {COVERAGE_PERCENTAGE}%
```

---

## Success ✅

All test cases successfully updated in Azure DevOps with automation details.
```

---

## Human-in-the-Loop

**Gate**: Before updating ADO

**User Actions**:
1. Review test case updates preview
2. Verify PR URL is correct
3. Check automation status field mapping
4. Approve ADO updates

**User Options**:
- ✅ Approve → Update all test cases in ADO
- 🔄 Edit Updates → Modify description template
- 🎯 Selective Update → Choose specific test cases to update
- ❌ Cancel → Skip ADO updates

---

## Error Handling

### Test Case Not Found
- Verify test case ID exists in ADO
- Check if test case was deleted
- Skip and continue with remaining test cases

### Permission Denied
- Verify PAT has "Work Items (Write)" permission
- Check user has edit access to test cases
- Request proper permissions

### Field Not Available
- Check if "Automation Status" field exists in ADO
- Use custom field if standard field unavailable
- Document which fields were skipped

### PR Link Invalid
- Verify PR was created successfully
- Check PR URL format
- Re-run `@pr-creator` if needed

---

## ADO Fields Updated

| Field | Value | Notes |
|-------|-------|-------|
| Automation Status | "Automated" | Standard ADO field |
| Description | Appended | Preserves existing content |
| Tags | +"; Automated" | Appends to existing tags |
| Comments | New comment | Tracking automation |
| Links | Link to PR | Related work item link |

---

## Validation

After updates, verify:

```bash
# Fetch updated test case from ADO
mcp__azure_devops__wit_work_item(work_item_id=123456)

# Check fields:
# - AutomationStatus = "Automated"
# - Description contains PR link
# - Tags include "Automated"
# - Comments include automation comment
# - Links include PR
```

---

## Success Criteria

✅ All test cases in mapping updated  
✅ Automation Status set correctly  
✅ PR links added to descriptions  
✅ Test file paths added  
✅ Comments added with run instructions  
✅ Test cases linked to PR  
✅ PBI updated with automation summary  
✅ Update summary report generated  
✅ User verified updates in ADO

---

## Output Files

```
automation/
└── working/
    └── ado-update-summary.md      ← Update summary report

Azure DevOps:
├── Test Cases (Updated with automation details)
├── PBI #{PBI_ID} (Updated with automation summary)
└── PR #{PR_ID} (Linked to test cases)
```

---

## Complete Workflow Summary

At this point, the complete automation workflow is finished:

1. ✅ Test cases fetched from ADO
2. ✅ Automation code generated
3. ✅ Pull Request created
4. ✅ ADO test cases updated with automation links

**Final Deliverables**:
- Automation test code in repository
- Pull Request ready for review
- ADO test cases marked as "Automated"
- Complete traceability: ADO ↔ Code ↔ PR

---

**Workflow Complete** ✅
