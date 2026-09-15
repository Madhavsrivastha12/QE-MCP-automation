# QA Understanding Document Template Update

## Date: 2026-08-23

## Changes Made

### Old Format (13 Sections - DEPRECATED)
The agent previously generated a generic 13-section document:
1. Feature Overview
2. Acceptance Criteria (simple list)
3. API Integration
4. Database Schema
5. Business Logic
6. Integration Points
7. Test Data Requirements
8. Environment Configuration
9. Risk Areas
10. Test Scenarios Summary
11. Dependencies and Assumptions
12. Open Questions
13. References
+ Appendix A & B

**Problems**:
- Too generic and template-like
- Examples used placeholders instead of real data
- QA interpretations were not specific to the PBI
- Didn't match the company's actual template format

### New Format (5 Sections - CURRENT)
Based on template: `C:\Users\TI\Downloads\QA-Understanding-Document-LongTerm-Forecast-Backcast-661604-updated_WithExample 1.docx`

1. **User Story** - "As a..., I want..., so that..." format
2. **Acceptance Criteria → QA Interpretation** - Given/When/Then format with:
   - QA interpretation (specific to PBI)
   - Concrete examples (real data, not placeholders)
3. **Business Rule → Data Mapping** (Table) - Maps rules to actual data sources:
   - Area | Business Rule | Source/Data Needed | Expected Behavior | AC
4. **Functional Flow** - Numbered steps using actual component/API/table names
5. **Constraints** - Specific gaps and open questions

## Key Improvements

### 1. Specificity Requirements
**OLD** (generic):
```
QA interpretation: Verify that the system displays the date correctly.
Example: A date is converted to the user's timezone.
```

**NEW** (specific):
```
QA interpretation: Verify that the last_forecasted_date from forecast_model table (stored as UTC timestamp) is correctly converted to the user's browser timezone and displayed in 12-hour format. The system must detect the user's timezone automatically and apply the conversion.

Example: POD 'CNP_POD123' has best_forecast_id = 5678. The forecast_model table shows last_forecasted_date = '2026-08-19 18:45:00 UTC'. A user in Central Daylight Time (UTC-5) views the POD Details table and sees "1:45 PM CDT". A user in EDT sees "2:45 PM EDT".
```

### 2. Business Rule Mapping Table
NEW section that maps business rules to actual data sources:

| Area | Business Rule | Source / Data Needed | Expected Behavior | AC |
|------|---------------|---------------------|-------------------|-----|
| Timezone Conversion | Convert UTC to local 12hr | forecast_model.last_forecasted_date, user timezone | UTC '2026-08-19 18:45:00' → '1:45 PM CDT' | AC2 |

### 3. Concrete Examples
- Use real POD names, dates, timestamps
- Show actual data transformations
- Include timezone-specific examples
- Reference actual table/column names from integration docs

### 4. Integration with Technical Docs
The agent now extensively uses `integration-docs.json` to:
- Reference actual API endpoints
- Use actual database table.column names
- Show actual request/response structures
- Map business rules to implementation details

## Files Updated

- `.claude/agents/qa_understanding_doc_creator.md` - Complete rewrite of Steps 3-9
  - New 5-section template structure
  - Specificity requirements added
  - Concrete example guidance
  - Business Rule table format
  - Removed old 13-section references

## Dependencies Installed

- `python-docx` - For Word document generation
- `openpyxl` - For Excel file generation (used by other agents)

Added to `requirements.txt` for future use.

## Usage

The agent will now automatically follow the new template when invoked:
```bash
@qa-understanding-doc-creator --pbi 645352
```

Output will be:
- `outputs/645352/deliverables/QA_Understanding_Document.docx` (5 sections, specific content)

## Template Reference

Original template location:
`C:\Users\TI\Downloads\QA-Understanding-Document-LongTerm-Forecast-Backcast-661604-updated_WithExample 1.docx`

This template should be used as the reference for all future QA Understanding Documents.

## Quality Checks

Before finalizing any QA Understanding Document, verify:
- [ ] User Story in "As a..., I want..., so that..." format
- [ ] All ACs have Given/When/Then structure
- [ ] QA interpretations reference actual table/column/API names
- [ ] Examples use concrete data (real dates, POD names, timestamps)
- [ ] Business Rule table maps to actual sources from integration-docs.json
- [ ] Functional Flow shows actual components and data flow
- [ ] Constraints list specific gaps (not generic "need more info")
- [ ] NO generic placeholders or template-like content
- [ ] Document is exactly 5 sections (not 13)

## Testing

To regenerate the QA Understanding Document for PBI 645352 with the new template:
```bash
# The orchestrator will automatically use the updated agent
@qa-workflow 645352
```

Or directly:
```bash
@qa-understanding-doc-creator --pbi 645352
```

Expected improvement: Document will have specific QA interpretations with concrete examples based on actual POD Details, forecast_model table, timezone conversion logic, etc.