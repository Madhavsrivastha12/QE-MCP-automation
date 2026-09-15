# PERMANENT QA UNDERSTANDING DOCUMENT STANDARD

**Status**: LOCKED - Applied to all current and future PBIs
**Last Updated**: 2026-08-27
**Generator**: `final_10_section_generator.py`

---

## DOCUMENT STRUCTURE

### 1. Feature Overview
- Feature name
- PBI number
- State
- Sprint/Iteration
- User Story (As a... I want... So that...)
- Background (PBI description)
- Key Business Value
- Scope (In Scope / Out of Scope)

### 2. Acceptance Criteria Breakdown

For **EVERY** Acceptance Criterion:
```
AC-X: [Title]

Given: [precondition]
When: [action]
Then: [expected result]

QA Interpretation: [What QA needs to validate based on this AC]

Example: [Specific example demonstrating this AC]
```

---

## CONTENT RULES

### ✅ DO:
1. Use ONLY information supported by the PBI, acceptance criteria, and source documents
2. Make each AC's QA Interpretation unique and specific to that AC
3. Make each AC's Example unique and specific to that AC
4. Keep content professional, clear, and QA-focused
5. Use business-level terminology from the PBI
6. Explain what QA needs to validate based on actual requirements
7. Demonstrate AC clearly with input → processing → expected result

### ❌ DO NOT:
1. Invent database table names, column names, API endpoints, IDs
2. Invent technical implementation details not in the source
3. Add unnecessary disclaimers:
   - `[INFERRED - REQUIRES VERIFICATION]`
   - `[UNKNOWN]`
   - `[SOURCE-BACKED WHERE AVAILABLE]`
   - `[INTERPRETATION - MEDIUM CONFIDENCE]`
   - `[Note: ... illustrative examples only]`
   - `[Example / Illustration only]`
   - `[Note: values are illustrative]`
4. Copy the same QA Interpretation across multiple ACs
5. Copy the same Example across multiple ACs
6. Repeat Given/When/Then text multiple times
7. Fabricate technical details just to appear technical

---

## QUALITY STANDARDS

### Professional QA Engineer Tone
- Clear and specific
- PBI-focused
- Technically meaningful where supported by source
- No unnecessary warnings
- No repetitive content
- No fabricated implementation details

### Content Validation (Internal Checklist)
Before generating, validate:
- [ ] Is every statement supported by PBI/source?
- [ ] Did I invent any technical detail?
- [ ] Does every AC have unique QA interpretation?
- [ ] Does every AC have a PBI-specific example?
- [ ] Did I remove unnecessary disclaimers?
- [ ] Did I avoid repetitive notes?
- [ ] Is the document professional and QA-focused?

**Rule**: If a detail is unsupported, omit it rather than adding a disclaimer.

---

## FORMATTING STANDARD

### Colors (RGB)
- **Title**: RGB(0, 51, 102) - Dark blue, 26pt, bold, center
- **Heading 1**: RGB(54, 95, 145) - Medium blue, 14pt, bold
- **Heading 2**: RGB(79, 129, 189) - Light blue, 13pt, bold
- **Body**: Calibri 11pt, line spacing 1.15

### Spacing
- Title space after: 12pt
- H1 space before: 12pt, space after: 6pt
- H2 space before: 10pt, space after: 4pt
- Paragraph space after: 6pt

### Page Setup
- Margins: 1 inch (2.54cm) all sides
- Size: Letter (8.5" x 11")
- Orientation: Portrait

---

## EXAMPLES

### ❌ WRONG (Generic, Invented Details, Disclaimers)

```
AC-1: Display Last Forecasted Date

Given a POD exists
When user views POD Details
Then last forecast date is shown

QA Interpretation: [SOURCE-BACKED WHERE AVAILABLE] The backend must query 
pod_header.best_forecast_id to identify the Best Forecast, then retrieve 
forecast_model.last_forecasted_date for that forecast_id. [Note: Table/field 
names are inferred from typical database schema - verify actual implementation]

Example / Illustration only — values are not source-verified:
POD 'CNP_POD_12345' has best_forecast_id = 98765 in the pod_header table.
[Note: Pod ID, forecast ID, and timestamps are illustrative examples only]
```

**Problems**:
- Invented table names (pod_header, forecast_model)
- Invented field names (best_forecast_id, last_forecasted_date)
- Unnecessary disclaimers throughout
- Generic QA interpretation

---

### ✅ CORRECT (Clean, Professional, PBI-Focused)

```
AC-1: Display Last Forecasted Date

Given: a POD has an associated Best Forecast
When: the POD Details page is loaded
Then: the POD Details table shall display the Last Forecasted Date

QA Interpretation: The backend must query the database to identify the Best 
Forecast for the POD, retrieve the last forecasted date from that forecast 
record, and include it in the API response. The frontend must display this 
value in a new column in the POD Details table.

Example: A POD has an associated Best Forecast with a last forecasted date 
of '2026-08-10T14:35:22.000Z'. When the POD Details page loads, the API 
returns this timestamp, and the POD Details table displays the Last 
Forecasted Date value in the user's local timezone format.
```

**Why This Is Correct**:
- Clean Given/When/Then format (appears once)
- QA Interpretation explains what to validate without inventing details
- Example demonstrates the AC clearly
- No unnecessary disclaimers
- Professional and specific

---

## AC-SPECIFIC CONTENT REQUIREMENT

### PBI 643243 Example

**AC-1**: Use Custom Forecast Upload Date as Max Read Date
- **Focus**: Data sourcing logic (upload date used as maxReadDate)
- **QA Interpretation**: Explains the data source selection behavior
- **Example**: Demonstrates using upload timestamp as Max Read Date

**AC-2**: Send Upload Timestamp in Response
- **Focus**: Outbound payload behavior (timestamp in response field)
- **QA Interpretation**: Explains the payload population requirement
- **Example**: Demonstrates timestamp appearing in outbound payload

**MUST NOT**: Reuse AC-1's interpretation/example for AC-2

### PBI 645352 Example

**AC-1**: Display Last Forecasted Date
- **QA Interpretation**: Backend query + frontend display
- **Example**: POD with Best Forecast → page loads → displays date

**AC-2**: Display in Local Timezone 12hr Format
- **QA Interpretation**: UTC conversion + 12-hour format + timezone
- **Example**: UTC timestamp → different local times for different users

**MUST NOT**: Reuse AC-1's interpretation/example for AC-2

---

## PERMANENT BEHAVIOR

This standard applies automatically to:
1. ✅ PBI 645352 (6 ACs)
2. ✅ PBI 643243 (2 ACs)
3. ✅ Every PBI provided from now onward

**DO NOT** revert to:
- Disclaimer-heavy format
- Invented technical details
- Generic QA interpretations
- Repeated content across ACs

---

## VALIDATION

### Automated Validation Script
```bash
python scripts/validate_ac_content.py <PBI_NUMBER>
```

Checks:
- Each AC has unique QA Interpretation
- Each AC has unique Example
- No duplicate content across ACs

### Generator
```bash
python scripts/final_10_section_generator.py <PBI_NUMBER>
```

Output:
```
outputs/<PBI_NUMBER>/deliverables/QA_Understanding_Document_PBI_<PBI_NUMBER>.docx
```

---

## REFERENCE DOCUMENTS

**Visual Template**: `outputs/645352/deliverables/QA_Understanding_Document.docx`
- Heading colors, fonts, spacing
- Professional layout and formatting

**Quality References**:
- PBI 645352: 6 ACs, UI feature, timezone handling
- PBI 643243: 2 ACs, API behavior, Custom Forecast logic

Both are GOOD examples of the permanent standard.

---

## LOCKED STANDARD

**This standard is PERMANENT and will NOT change unless explicitly requested.**

All future PBIs automatically receive:
- Clean professional formatting
- PBI-specific unique AC content
- No unnecessary disclaimers
- No invented technical details
- Quality matching reference documents

**Date Locked**: 2026-08-27
**Generator Version**: final_10_section_generator.py (permanent)