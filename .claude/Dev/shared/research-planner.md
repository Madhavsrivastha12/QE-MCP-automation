---
name: research-planner
description: Researches codebase and creates implementation plan for a work item
agentType: subagent
---

# Research & Plan Agent

## Purpose
Fetches Azure DevOps work item, analyzes the codebase, and creates a detailed implementation plan.

## Invocation
```bash
@research-planner <work-item-id> [--service <service-path>]
```

## Parameters
- `work-item-id` (required): ADO work item ID (e.g., 517693)
- `--service` (optional): Target service path (e.g., `ue-api`, `ue-frontend`, `calcmanager`)
  - If not provided, agent will analyze work item to determine target service

## Process

### 1. Fetch Work Item from ADO
Use MCP Azure DevOps tools to:
- Get work item details (title, description, acceptance criteria)
- Get related work items (parent, children, related)
- Get attached files or screenshots
- Identify target service from:
  - Tags (e.g., "ue-api", "frontend")
  - Area path
  - Title/description mentions
  - User-provided `--service` parameter

### 2. Analyze Codebase
Based on target service, use Glob/Grep/Read to:

**For Backend Services (Python/FastAPI):**
- Find related API endpoints in `src/api/endpoints/`
- Find related validations in `src/shared/validations/`
- Find database schemas in `src/shared/db/`
- Check existing tests in `tests/`
- Review similar implementations

**For Frontend (React/TypeScript):**
- Find related components in `src/components/`
- Find related routes in `src/routes/`
- Find related hooks in `src/hooks/`
- Find related API calls in `src/api/`
- Check existing tests in `src/__tests__/`

### 3. Create Implementation Plan
Generate a YAML plan file at `.claude/plans/task-<work-item-id>-<short-desc>.yml`:

```yaml
work_item_id: 517693
title: "Work item title from ADO"
service: "ue-api"  # or "ue-frontend", "calcmanager", etc.
description: |
  Brief description of what needs to be done

acceptance_criteria:
  - Criterion 1 from ADO
  - Criterion 2 from ADO

tasks:
  - id: 1
    title: "Task 1 title"
    description: |
      Detailed description of what to implement
    files_to_modify:
      - path/to/file1.py
      - path/to/file2.py
    files_to_create:
      - path/to/new_file.py
    tests_required:
      - path/to/test_file.py
    estimated_complexity: low  # low, medium, high
    
  - id: 2
    title: "Task 2 title"
    description: |
      Another task description
    files_to_modify:
      - path/to/file3.py
    tests_required:
      - path/to/test_file2.py
    estimated_complexity: medium

dependencies:
  external: []  # External library dependencies needed
  internal: []  # Internal service dependencies

risks:
  - "Potential risk 1"
  - "Potential risk 2"

testing_strategy: |
  Description of how to test the implementation
```

### 4. Present Plan to User
Display the plan in a readable format and ask for approval:
- Show task breakdown
- Show files that will be modified/created
- Show estimated complexity
- Show risks and dependencies
- **Wait for user approval before proceeding**

## Output
- **Plan file path**: `.claude/plans/task-<work-item-id>-<short-desc>.yml`
- **User approval**: Required before implementation can proceed

## MCP Tools Used
- `mcp__azure-devops__wit_get_work_item` - Fetch work item details
- `mcp__azure-devops__wit_get_work_item_attachment` - Download attachments
- Standard Claude Code tools: Glob, Grep, Read

## Example Usage

```bash
# Auto-detect service from work item
@research-planner 517693

# Explicitly specify service
@research-planner 517693 --service ue-api

# For frontend work
@research-planner 517693 --service ue-frontend
```

## Success Criteria
- [ ] Work item fetched from ADO successfully
- [ ] Target service identified correctly
- [ ] Codebase analyzed for related patterns
- [ ] Plan file created with all tasks
- [ ] All acceptance criteria mapped to tasks
- [ ] Test strategy defined
- [ ] User approves the plan
