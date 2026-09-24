---
name: pr-creator
description: Create Pull Request with generated automation test code
tools: ["*"]
---

# PR Creator Agent

## Purpose
Create a Pull Request in Azure DevOps with the generated automation test code, linking it back to the original PBI.

## Input
- Generated test files in `automation/tests/`
- `automation/working/test-mapping.json`
- PBI metadata (ID, title, URL)

## Output
- Git branch: `automation/pbi-{id}`
- Pull Request created in Azure DevOps
- PR URL returned
- PR linked to PBI

---

## Process

### Step 1: Verify Test Files Exist

Check that automation code has been generated:
```bash
# Verify test files exist
ls -R automation/tests/

# Expected structure:
# automation/tests/ui/*.spec.ts
# automation/tests/api/test_*.py
# automation/tests/database/test_*.py
```

### Step 2: Create Feature Branch

```bash
# Get current branch
git branch --show-current

# Create automation branch from main
git checkout -b automation/pbi-{PBI_ID}

# Example: automation/pbi-643243
```

### Step 3: Stage Automation Files

```bash
# Stage all automation files
git add automation/

# Include config files
git add playwright.config.ts
git add pytest.ini
git add package.json
git add requirements.txt

# Verify staged files
git status
```

### Step 4: Create Commit

**Commit Message Template**:
```
Add automation tests for PBI #{PBI_ID}: {PBI_TITLE}

## Summary
Generated automation test code from Azure DevOps test cases.

## Test Coverage
- UI Tests (Playwright): {UI_COUNT} tests
- API Tests (Pytest): {API_COUNT} tests
- Database Tests (Pytest): {DB_COUNT} tests

## Test Files Added
{LIST_OF_TEST_FILES}

## ADO Test Cases Automated
{LIST_OF_ADO_TEST_CASE_IDS}

## Setup Instructions
See automation/README.md for setup and execution instructions.

## Related Work Items
- PBI #{PBI_ID}
- Test Cases: {TEST_CASE_IDS}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Example Commit**:
```bash
git commit -m "$(cat <<'EOF'
Add automation tests for PBI #643243: Implement User Authentication

## Summary
Generated automation test code from Azure DevOps test cases.

## Test Coverage
- UI Tests (Playwright): 15 tests
- API Tests (Pytest): 8 tests
- Database Tests (Pytest): 2 tests

## Test Files Added
- automation/tests/ui/login.spec.ts
- automation/tests/ui/registration.spec.ts
- automation/tests/api/test_auth_api.py
- automation/tests/api/test_user_api.py
- automation/tests/database/test_user_schema.py

## ADO Test Cases Automated
- Test Case #123456: Verify user login
- Test Case #123457: Verify user registration
- Test Case #123458: Verify password reset
... (15 more)

## Setup Instructions
See automation/README.md for setup and execution instructions.

## Related Work Items
- PBI #643243

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

### Step 5: Push Branch to Remote

```bash
# Push to remote with upstream tracking
git push -u origin automation/pbi-{PBI_ID}

# Verify push succeeded
git status
```

### Step 6: Create Pull Request

Use Azure DevOps MCP to create PR:

**PR Details**:
```json
{
  "title": "Automation Tests for PBI #{PBI_ID}: {PBI_TITLE}",
  "description": "{PR_DESCRIPTION}",
  "source_branch": "automation/pbi-{PBI_ID}",
  "target_branch": "main",
  "work_items": ["{PBI_ID}"],
  "reviewers": ["{TEAM_MEMBERS}"]
}
```

**PR Description Template**:
```markdown
# Automation Tests for PBI #{PBI_ID}

## 📋 Overview
This PR adds automated tests for PBI #{PBI_ID}: {PBI_TITLE}

**PBI Link**: {ADO_PBI_URL}

## ✅ Test Coverage Summary

| Test Type | Count | Framework | Status |
|-----------|-------|-----------|--------|
| UI Tests | {UI_COUNT} | Playwright | ✅ Generated |
| API Tests | {API_COUNT} | Pytest | ✅ Generated |
| Database Tests | {DB_COUNT} | Pytest | ✅ Generated |
| **Total** | **{TOTAL_COUNT}** | - | - |

## 📂 Files Added

### UI Tests (Playwright)
- `automation/tests/ui/login.spec.ts`
- `automation/tests/ui/registration.spec.ts`
- ...

### API Tests (Pytest)
- `automation/tests/api/test_auth_api.py`
- `automation/tests/api/test_user_api.py`
- ...

### Database Tests (Pytest)
- `automation/tests/database/test_user_schema.py`

### Supporting Files
- `automation/page-objects/LoginPage.ts`
- `automation/fixtures/api_client.py`
- `playwright.config.ts`
- `pytest.ini`
- `package.json`
- `requirements.txt`

## 🔗 ADO Test Cases Automated

This PR automates the following Azure DevOps test cases:

| ADO ID | Test Case Title | Test File | Type |
|--------|----------------|-----------|------|
| #123456 | Verify user login | login.spec.ts | UI |
| #123457 | Verify user API | test_user_api.py | API |
| ... | ... | ... | ... |

Complete mapping: `automation/working/test-mapping.json`

## 🚀 How to Run Tests

### Prerequisites
```bash
# Install Node.js dependencies (for Playwright)
npm install

# Install Python dependencies (for Pytest)
pip install -r requirements.txt

# Install Playwright browsers
npx playwright install
```

### Run Tests
```bash
# All UI tests
npx playwright test

# All API tests
pytest automation/tests/api -v

# All database tests
pytest automation/tests/database -v

# Specific test file
npx playwright test login.spec.ts
```

### View Results
```bash
# Playwright HTML report
npx playwright show-report

# Pytest verbose output
pytest automation/tests/ -v --html=report.html
```

## ✨ Test Execution Strategy

- **CI/CD**: Tests will run automatically on PR and merge to main
- **Environment**: Tests configured for DEV environment
- **Data**: Test data located in `automation/test-data/`
- **Parallel**: UI tests run in parallel (configured in playwright.config.ts)

## 📝 Review Checklist

- [ ] All test files follow naming conventions
- [ ] Page objects are properly structured
- [ ] Test data is externalized
- [ ] Selectors use data-testid attributes
- [ ] Tests include proper assertions
- [ ] Each test maps to an ADO test case
- [ ] README includes setup instructions
- [ ] CI/CD pipeline configured

## 🔗 Related Work Items

- PBI #{PBI_ID}: {PBI_TITLE}
- Test Cases: #{TEST_CASE_IDS}

## 📸 Screenshots (if applicable)

_Add screenshots of test execution results here_

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**MCP Tool Call**:
```python
# Use Azure DevOps MCP to create PR
mcp__azure_devops__repo_pull_request_write(
    repository_id="{REPO_ID}",
    source_branch="refs/heads/automation/pbi-{PBI_ID}",
    target_branch="refs/heads/main",
    title="Automation Tests for PBI #{PBI_ID}: {PBI_TITLE}",
    description=pr_description,
    work_item_refs=[{"id": PBI_ID}]
)
```

### Step 7: Generate PR Summary Report

Create `automation/working/pr-summary.md`:

```markdown
# Pull Request Created Successfully

**PR URL**: {PR_URL}

**Branch**: `automation/pbi-{PBI_ID}`

**Status**: Open and ready for review

## PR Details
- **Title**: Automation Tests for PBI #{PBI_ID}
- **Source**: automation/pbi-{PBI_ID}
- **Target**: main
- **Linked Work Items**: PBI #{PBI_ID}

## Test Coverage
- UI Tests: {UI_COUNT}
- API Tests: {API_COUNT}
- Database Tests: {DB_COUNT}
- **Total**: {TOTAL_COUNT} automated tests

## Next Steps
1. PR reviewers have been notified
2. Wait for code review approval
3. After approval, proceed with `@ado-link-updater` to update ADO test cases
4. Merge PR after successful review and tests pass

## Files Changed
- {FILE_COUNT} files added
- {LINE_COUNT} lines of code

## CI/CD Status
- Pipeline: {PIPELINE_STATUS}
- Tests: {TEST_STATUS}
```

---

## Human-in-the-Loop

**Gate**: Before creating PR

**User Actions**:
1. Review PR description
2. Verify all test files are included
3. Check commit message
4. Approve PR creation

**User Options**:
- ✅ Approve → Create PR in Azure DevOps
- 🔄 Edit PR Description → Modify template before creation
- 🔁 Re-stage Files → Adjust which files to include
- ❌ Cancel → Stop workflow

---

## Error Handling

### Git Push Failed
- Check for merge conflicts
- Verify remote branch doesn't exist
- Ensure user has push permissions

### PR Creation Failed
- Verify Azure DevOps PAT permissions
- Check if branch already has open PR
- Validate work item IDs exist

### Missing Files
- Verify automation code was generated
- Check working directory is correct
- Re-run `@automation-code-generator`

---

## Branch Naming Convention

```
automation/pbi-{PBI_ID}
```

**Examples**:
- `automation/pbi-643243`
- `automation/pbi-634367`

**Why This Pattern?**
- Clear purpose: "automation" prefix
- Traceable: PBI ID in branch name
- Searchable: Easy to find in git history
- Consistent: Matches existing conventions

---

## PR Reviewers

**Default Reviewers**:
- QA Team Lead
- Automation Engineer
- Original PBI assignee

**Optional Reviewers**:
- DevOps Engineer (for CI/CD changes)
- Developer (for technical validation)

---

## CI/CD Integration

**Expected Pipeline**:
```yaml
# .github/workflows/automation-tests.yml
name: Automation Tests

on:
  pull_request:
    paths:
      - 'automation/**'

jobs:
  ui-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: npm install
      - name: Run Playwright tests
        run: npx playwright test
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/

  api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run Pytest
        run: pytest automation/tests/api -v
```

---

## Success Criteria

✅ Branch created successfully  
✅ All automation files committed  
✅ Branch pushed to remote  
✅ PR created in Azure DevOps  
✅ PR linked to PBI  
✅ Reviewers assigned  
✅ PR summary report generated  
✅ User approved PR

---

## Output Files

```
automation/
└── working/
    └── pr-summary.md         ← PR creation summary

Git:
└── Branch: automation/pbi-{PBI_ID}
    └── PR: {PR_URL}
```

---

**Next Agent**: `ado_link_updater.md`
