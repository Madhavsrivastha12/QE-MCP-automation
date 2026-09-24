# QA Manual Testing Workflow Agents

This folder contains agents for the QA Manual Testing documentation workflow. The workflow is divided into two phases:

## Workflow Overview

```
Phase 1: Initial Documentation
├── Understanding Document (from PBI Acceptance Criteria)
└── Test Scenarios (from Understanding Document)

Phase 2: Enhanced Documentation  
├── Understanding Document (enhanced with Manual Documentation from Dev)
├── Test Scenarios (enhanced with technical details)
└── Test Cases (uploaded to Azure DevOps Test Plans)
```

---

## Phase 1: Initial Documentation

### 1. Understanding Document Generator
**Agent**: `phase1_initial/ud_from_acceptance_criteria.md`

**Purpose**: Generate initial Understanding Document from PBI Acceptance Criteria

**Input**: 
- PBI ID (fetched from Azure DevOps)

**Output**:
- `understanding_documents/QA Understanding Document - PBI {id}.docx`
- Committed to git and attached to PBI

**Process**:
1. Fetch PBI from Azure DevOps
2. Generate Understanding Document with sections:
   - User Story
   - Acceptance Criteria → QA Interpretation
   - Key Data Sources & Tables
   - Schema Reference
   - Regression Risk Summary
   - Test Environment Prerequisites
3. Human-in-the-Loop: User reviews and edits
4. Commit to git and attach to PBI

---

### 2. Test Scenarios Generator
**Agent**: `phase1_initial/ts_from_understanding_doc.md`

**Purpose**: Generate initial Test Scenarios from Understanding Document

**Input**:
- Understanding Document DOCX

**Output**:
- `test_scenarios/Draft 1 Test Scenarios - PBI {id}.xlsx`
- User manages git commits manually

**Process**:
1. Read Understanding Document
2. Generate Excel with 2 sheets:
   - Sheet 1: Test Scenarios (AC#, Title, Scenario ID, Steps, Expected Results, Priority)
   - Sheet 2: AC to Scenario Mapping
3. Human-in-the-Loop: User reviews and edits
4. User commits manually to git

---

## Phase 2: Enhanced Documentation

### 3. Understanding Document Enhancer
**Agent**: `phase2_final/ud_with_manual_documentation.md`

**Purpose**: Enhance Understanding Document with Manual Documentation from developers

**Input**:
- Initial Understanding Document DOCX
- Manual Documentation (.md file from developer - user provides path)

**Output**:
- `understanding_documents/Final QA Understanding Document - PBI {id}.docx`
- Preserves initial UD
- Committed to git and replaces PBI attachment

**Process**:
1. Read initial Understanding Document
2. Read Manual Documentation from developer
3. Enhance all sections with technical details:
   - Schema details (complete DDL)
   - API specifications
   - Configuration details
   - Performance considerations
4. Human-in-the-Loop: User reviews and edits
5. Commit to git and replace PBI attachment

---

### 4. Test Scenarios Enhancer
**Agent**: `phase2_final/ts_with_technical_details.md`

**Purpose**: Enhance Test Scenarios with technical details from Final Understanding Document

**Input**:
- Final Understanding Document DOCX
- Initial Test Scenarios Excel

**Output**:
- `test_scenarios/Final Test Scenarios - PBI {id}.xlsx`
- Preserves initial Test Scenarios
- User manages git commits manually

**Process**:
1. Read Final Understanding Document
2. Read initial Test Scenarios
3. Enhance each scenario with:
   - Specific table/column names
   - Actual SQL queries
   - API endpoints and payloads
   - Configuration settings
   - Detailed expected results
4. Add new scenarios from Final UD insights
5. Human-in-the-Loop: User reviews and edits
6. User commits manually to git

---

### 5. Test Cases Creator
**Agent**: `phase2_final/tc_for_ado_test_plans.md`

**Purpose**: Create Test Cases for Azure DevOps Test Plans

**Input**:
- Final Understanding Document DOCX
- Final Test Scenarios Excel
- PBI metadata (Area Path, Assigned To)

**Output**:
- `test_cases/Final Test Cases - PBI {id}.xlsx`
- Test Cases uploaded to Azure DevOps Test Plans
- Excel committed to git and attached to PBI

**Process**:
1. Fetch PBI metadata (Area Path, Assigned To)
2. Read Final Test Scenarios
3. Generate Test Cases Excel with columns:
   - ID, Work Item Type, Title, Test Step, Step Action, Step Expected, Area Path, Assigned To, State
   - Each Test Scenario becomes 1 Test Case with multiple step rows
4. Human-in-the-Loop: User reviews and edits
5. Upload Test Cases to Azure DevOps Test Plans
6. Commit Excel to git and attach to PBI

---

## Repository Structure

```
QE-MCP-automation/
├── .claude/agents/qa-manual/
│   ├── phase1_initial/
│   │   ├── ud_from_acceptance_criteria.md
│   │   └── ts_from_understanding_doc.md
│   ├── phase2_final/
│   │   ├── ud_with_manual_documentation.md
│   │   ├── ts_with_technical_details.md
│   │   └── tc_for_ado_test_plans.md
│   └── README.md (this file)
├── understanding_documents/
│   ├── QA Understanding Document - PBI {id}.docx (Initial)
│   └── Final QA Understanding Document - PBI {id}.docx
├── test_scenarios/
│   ├── Draft 1 Test Scenarios - PBI {id}.xlsx (Initial)
│   └── Final Test Scenarios - PBI {id}.xlsx
├── test_cases/
│   └── Final Test Cases - PBI {id}.xlsx
└── manual_docs/
    └── (MD files from developers)
```

---

## Complete Workflow Sequence

1. **Generate Understanding Document** (Phase 1)
   - Input: PBI ID
   - Output: Initial Understanding Document
   - Action: Committed + Attached to PBI

2. **Generate Test Scenarios** (Phase 1)
   - Input: Initial Understanding Document
   - Output: Initial Test Scenarios
   - Action: User commits manually

3. **Enhance Understanding Document** (Phase 2)
   - Input: Initial UD + Manual Documentation
   - Output: Final Understanding Document
   - Action: Committed + Replaces PBI attachment

4. **Enhance Test Scenarios** (Phase 2)
   - Input: Final UD + Initial Test Scenarios
   - Output: Final Test Scenarios
   - Action: User commits manually

5. **Create Test Cases** (Phase 2)
   - Input: Final UD + Final TS + PBI metadata
   - Output: Final Test Cases + ADO Test Cases
   - Action: Upload to ADO + Commit + Attach to PBI

---

## Human-in-the-Loop Gates

Every agent includes a Human-in-the-Loop approval gate:
- Agent generates draft output
- **User reviews and edits** the output
- User approves before agent proceeds with git/ADO actions

This ensures QA engineers maintain full control over quality and accuracy.

---

## Tools & Technologies

- **Azure DevOps MCP Tools**: Fetch PBIs, attach files, create Test Cases
- **python-docx**: Read/write DOCX files
- **openpyxl/xlsxwriter**: Read/write Excel files
- **Git**: Version control and collaboration
- **Azure DevOps Test Plans**: Test execution platform
