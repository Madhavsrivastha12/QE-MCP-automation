---
name: qa-workflow
description: >
  Short alias for qa-workflow-orchestrator. Executes complete QA testing workflow from PBI fetch to test case generation.
  Usage: @qa-workflow <PBI_NUMBER>
---

# QA Workflow - Quick Command Alias

This is a **short alias** for the full `qa-workflow-orchestrator` agent.

## Usage

```bash
@qa-workflow <PBI_NUMBER>
```

**Example**:
```bash
@qa-workflow 643243
```

## What It Does

Executes the complete 5-phase QA workflow:

1. **Phase 1**: Collect scope (test type(s), component(s), supporting
   documentation path(s), additional info) → `user-context.json`;
   fetch PBI from Azure DevOps → `pbi-data.json`
2. **Phase 2**: Read **only the documents the user provided** → `integration-docs.json`
   (written even when the user provides none, with empty buckets + gaps)
3. **Phase 3**: Create QA Understanding Document → `QA_Understanding_Document.docx` (Word format)
4. **Phase 4**: Map test scenarios to AC → `Test-Scenarios-Mapped-to-AC.xlsx`
5. **Phase 5**: Generate test cases → `Test_Cases.xlsx`

With 2 user checkpoints for review and approval between phases 3-4 and 4-5.

## Implementation

When invoked, immediately delegate to the full orchestrator agent:

```
Agent({
  description: "Execute QA workflow for PBI",
  prompt: "Execute the complete QA workflow orchestrator for PBI {pbi_number}. Follow all 5 phases with user checkpoints as defined in the qa-workflow-orchestrator agent.",
  subagent_type: "qa-workflow-orchestrator"
})
```

## Output Location

All files saved to: `outputs/<PBI_NUMBER>/`

Example for PBI 643243:
```
outputs/643243/
├── deliverables/                           ← final, user-facing QA output
│   ├── QA_Understanding_Document.docx      ← Phase 3
│   ├── Test-Scenarios-Mapped-to-AC.xlsx    ← Phase 4
│   ├── Test_Cases_PBI_643243.xlsx          ← Phase 5
│   ├── ui/                                 ← ONLY when "UI" selected
│   └── db/                                 ← ONLY when "Database" selected
├── working/                                ← intermediate artifacts
│   ├── pbi-data.json                       ← Phase 1 (ADO data)
│   ├── user-context.json                   ← Phase 1 (scope contract)
│   └── integration-docs.json               ← Phase 2
└── logs/                                   ← phase reports, validation, debug
    └── 00-WORKFLOW-SUMMARY.md              ← Summary report
```

## Deliverables

- **QA Understanding Document**: Professional Word document with 10 sections, navy blue formatting, dynamic QA interpretations, complete AC text (no truncation)
- **Test Scenario Mapping**: Excel file mapping scenarios to AC with categorization
- **Test Cases**: Azure DevOps import-ready Excel format with detailed test steps

## Formatting Standards

The QA Understanding Document follows **permanent formatting standards**:
- ✅ Complete text preservation (NO "..." truncation)
- ✅ Auto-wrapped long AC headings across multiple lines
- ✅ Professional Word template (navy blue color scheme)
- ✅ Smart page break control (no orphan headings)
- ✅ Dynamic page numbers ("Page X of Y | Generated: date")
- ✅ Implementation-focused QA interpretations (explains HOW and WHAT)
- ✅ Concrete examples with real dates/timestamps
- ✅ Professional tables with navy blue headers

## Notes

- This skill is purely an **alias** for easier invocation
- All functionality is in the `qa-workflow-orchestrator` agent
- No changes to workflow logic or agent coordination
- User can use either `@qa-workflow` or `@qa-workflow-orchestrator` interchangeably

## Full Documentation

For complete workflow details, checkpoints, error handling, and resume options, see:
`.claude/agents/qa_workflow_orchestrator.md`

---

**End of Skill Definition**
