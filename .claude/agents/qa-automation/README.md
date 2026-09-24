# QA Automation Testing Workflow Agents

This folder contains agents for the QA Automation Testing workflow. This workflow generates automation test code from existing Azure DevOps Test Cases.

## Workflow Overview

```
ADO Test Cases (Input)
   ↓
Step 1: Fetch Test Cases from ADO
   ↓
Step 2: Generate Automation Code (Playwright/Pytest)
   ↓
Step 3: Create Pull Request
   ↓
Step 4: Update ADO with Automation Links
```

---

## Agents

### 1. Test Case Fetcher
**Agent**: `test_case_fetcher.md`

**Purpose**: Fetch test cases from Azure DevOps Test Plans

**Input**: 
- PBI ID or Test Suite ID

**Output**:
- `automation/working/ado-test-cases.json`

**Process**:
1. Fetch test cases from Azure DevOops using MCP tools
2. Parse test case structure (Title, Steps, Expected Results)
3. Save to JSON for automation generation

---

### 2. Automation Code Generator
**Agent**: `automation_code_generator.md`

**Purpose**: Generate automation test code from ADO test cases

**Input**:
- `automation/working/ado-test-cases.json`

**Output**:
- `automation/tests/` - Generated test files (Playwright/Pytest)
- Test framework setup files (pytest.ini, playwright.config.ts)

**Process**:
1. Read ADO test cases JSON
2. Determine test type (UI/API/Database)
3. Generate appropriate test code:
   - UI tests: Playwright TypeScript
   - API tests: Pytest + requests
   - Database tests: Pytest + SQLAlchemy
4. Create page objects/fixtures as needed
5. Generate test data files

---

### 3. PR Creator
**Agent**: `pr_creator.md`

**Purpose**: Create Pull Request with generated automation code

**Input**:
- Generated test files in `automation/tests/`
- PBI metadata

**Output**:
- Git branch created
- Pull Request in Azure DevOps
- PR URL returned

**Process**:
1. Create feature branch `automation/pbi-{id}`
2. Stage generated test files
3. Commit with descriptive message
4. Push to remote
5. Create PR using Azure DevOps MCP
6. Link PR to original PBI

---

### 4. ADO Link Updater
**Agent**: `ado_link_updater.md`

**Purpose**: Update ADO Test Cases with links to automation code

**Input**:
- Test case IDs from ADO
- PR URL
- File paths of automation tests

**Output**:
- ADO Test Cases updated with:
  - "Automation Status" field set to "Automated"
  - Link to PR in description
  - Link to test file path

**Process**:
1. Read test case mappings (ADO ID → Test file)
2. For each test case, update ADO using MCP:
   - Add PR link to description
   - Add automation file path
   - Set automation status field
3. Generate summary report

---

## Repository Structure

```
QE-MCP-automation/
├── .claude/agents/qa-automation/
│   ├── test_case_fetcher.md
│   ├── automation_code_generator.md
│   ├── pr_creator.md
│   ├── ado_link_updater.md
│   └── README.md (this file)
│
├── automation/
│   ├── working/
│   │   ├── ado-test-cases.json
│   │   └── test-mapping.json (ADO ID → Test file)
│   ├── tests/
│   │   ├── ui/           # Playwright UI tests
│   │   ├── api/          # Pytest API tests
│   │   └── database/     # Pytest DB tests
│   ├── fixtures/         # Test fixtures and helpers
│   ├── page-objects/     # UI page objects
│   └── test-data/        # Test data files
│
└── .github/workflows/
    └── automation-tests.yml  # CI/CD pipeline
```

---

## Complete Workflow Sequence

1. **Fetch Test Cases from ADO**
   - Input: PBI ID or Test Suite ID
   - Output: `automation/working/ado-test-cases.json`

2. **Generate Automation Code**
   - Input: `ado-test-cases.json`
   - Output: Test files in `automation/tests/`
   - Human-in-the-Loop: Review generated code

3. **Create Pull Request**
   - Input: Generated test files
   - Output: PR in Azure DevOps
   - Action: Branch created and pushed

4. **Update ADO Test Cases**
   - Input: PR URL + Test mappings
   - Output: ADO Test Cases updated with automation links

---

## Human-in-the-Loop Gates

Every agent includes approval gates:
- **Step 2**: User reviews generated automation code before PR
- **Step 3**: User reviews PR description before creation
- **Step 4**: User confirms ADO updates before execution

This ensures QA engineers maintain control over automation quality.

---

## Test Frameworks Supported

- **UI Testing**: Playwright (TypeScript)
- **API Testing**: Pytest + Requests (Python)
- **Database Testing**: Pytest + SQLAlchemy (Python)

---

## Tools & Technologies

- **Azure DevOps MCP Tools**: Fetch test cases, create PRs, update work items
- **Git**: Version control
- **Playwright**: UI automation
- **Pytest**: Python testing framework
- **Requests**: API testing
- **SQLAlchemy**: Database testing

---

## Usage Examples

### Example 1: Generate automation for entire PBI
```bash
@qa-automation-workflow 643243
```

### Example 2: Generate automation for specific test suite
```bash
@qa-automation-workflow --suite-id 12345
```

### Example 3: Manual step-by-step
```bash
# Step 1: Fetch test cases
@test-case-fetcher 643243

# Step 2: Generate code
@automation-code-generator automation/working/ado-test-cases.json

# Step 3: Create PR
@pr-creator automation/tests/

# Step 4: Update ADO
@ado-link-updater --pr-url https://dev.azure.com/...
```

---

## Configuration

### Framework Selection
Edit `automation/config.json`:
```json
{
  "ui_framework": "playwright",
  "api_framework": "pytest",
  "test_data_format": "json",
  "auto_generate_fixtures": true
}
```

---

**Version**: 1.0.0  
**Last Updated**: 2026-09-23  
**Status**: Initial Setup
