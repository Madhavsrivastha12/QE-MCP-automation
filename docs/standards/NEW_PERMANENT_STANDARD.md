# NEW PERMANENT QA DOCUMENT STANDARD

## Status: ✓ LOCKED IN - Do Not Change Without Explicit Request

---

## TEMPLATE AND QUALITY REFERENCES

### Primary Visual Template
**Source**: `outputs/645352/deliverables/QA_Understanding_Document.docx`
- Heading colors (dark blue, medium blue, light blue)
- Font styles and sizes
- Spacing and layout
- Table formatting
- Page structure
- Professional presentation

### Quality References (Both GOOD Examples)
1. **PBI 645352** - Pod View Page Last Forecast Date
2. **PBI 643243** - Custom Forecast Max Read Date

**Purpose**: Understand expected level of detail, QA interpretation depth, example quality, and content structure

---

## CRITICAL PRINCIPLES

### 1. Visual Formatting = TEMPLATE
- Exact heading colors from template
- Same font family, sizes, weights
- Same spacing before/after headings
- Same table styling
- Same paragraph formatting
- Same page layout

### 2. Content Quality = REFERENCE PBIs
- Same level of technical detail
- Same QA interpretation depth
- Same example thoroughness
- Same professional tone
- Same clarity and organization

### 3. Content Specificity = PBI-ONLY
- ✅ Use only information from the current PBI
- ✅ Use integration docs for the current PBI
- ✅ Use comments/notes for the current PBI
- ❌ NEVER copy PBI-specific content from other PBIs
- ❌ NEVER hallucinate technical details
- ❌ NEVER invent table names, field names, API endpoints, or data values

### 4. Transparency = Mark Unverified Information
- **[SOURCE-BACKED]** - Information from PBI, integration docs, or code
- **[INTERPRETATION - MEDIUM CONFIDENCE]** - Logical interpretation of requirements
- **[INFERRED - REQUIRES VERIFICATION]** - Best guess based on patterns
- **[UNKNOWN - REQUIRES VERIFICATION]** - No information available

---

## DOCUMENT STRUCTURE

### Title Page
```
QA UNDERSTANDING DOCUMENT
[Title style: Dark blue RGB(0, 51, 102), 26pt, center, bold]

Feature: [PBI Title]
[Blue RGB(0, 102, 204), 14pt, center, bold]

PBI: [number] | State: [state] | Sprint: [iteration]
[Gray, 10pt, center]
```

### Section 1: Feature Overview

**1. Feature Overview** [Heading 1: Medium blue RGB(54, 95, 145), 14pt, bold]

**User Story** [Heading 2: Light blue RGB(79, 129, 189), 13pt, bold]
```
As a [role],
I want [feature],
So that I can [benefit].
```

**Background** [Heading 2]
[PBI description]

**Key Business Value** [Heading 2]
- [Business value 1]
- [Business value 2]
- [Mark as INFERRED if not explicitly documented]

**Scope** [Heading 2]
In Scope:
- [Item from each AC]

Out of Scope:
- [Items not covered]

### Section 2: Acceptance Criteria Breakdown

**2. Acceptance Criteria Breakdown** [Heading 1]

Intro paragraph explaining section structure.

**For EACH Acceptance Criterion:**

**AC-1: [Title]** [Heading 2]

```
Given [precondition]
When [action]
Then [expected result]
```

**QA Interpretation:** [Detailed, PBI-specific interpretation with technical details, data sources, validation requirements. Mark confidence level.]

**Example:** [Detailed, concrete example showing input → processing → output. Mark if values are illustrative vs source-verified.]

---

**AC-2: [Title]** [Heading 2]

[Repeat same pattern]

...

[Continue for ALL ACs]

---

## MANDATORY REQUIREMENTS

### Every AC Must Have:
1. ✅ Acceptance Criterion text (Given-When-Then if available)
2. ✅ QA Interpretation (detailed, PBI-specific)
3. ✅ Example (concrete, illustrative, with disclaimer if not source-verified)

### Order MUST Be:
```
AC Heading
  ↓
AC Text (Given-When-Then)
  ↓
QA Interpretation
  ↓
Example
```

**Never combine multiple ACs together**
**Never skip QA Interpretation**
**Never skip Example**

---

## QA INTERPRETATION REQUIREMENTS

### What to Include:
- Backend processing (which tables, which fields, which queries)
- Frontend processing (timezone conversion, formatting, display logic)
- Data sources (specific table and field names if known)
- Validation requirements (what QA must check)
- Integration points (API calls, database queries)
- Business logic (how the system determines behavior)

### Confidence Marking:
```
[SOURCE-BACKED WHERE AVAILABLE]
The backend must query pod_header.best_forecast_id to identify the Best Forecast...
[Note: Table/field names are inferred from typical schema - verify actual implementation]
```

```
[INTERPRETATION - MEDIUM CONFIDENCE]
The system must use a deterministic method to identify the Best Forecast...
Verify whether this uses best_forecast_id reference or is_best flag.
```

```
[UNKNOWN - REQUIRES VERIFICATION]
[No detailed technical documentation available - QA must verify implementation details]
```

### What NOT to Do:
- ❌ Generic "verify that the system correctly..." statements
- ❌ Repeating the AC text in different words
- ❌ Hallucinating table names, field names, or technical details
- ❌ Presenting assumptions as facts

---

## EXAMPLE REQUIREMENTS

### Every Example Must:
1. Show a concrete scenario
2. Include input/starting condition
3. Show relevant data (with disclaimer if illustrative)
4. Demonstrate the processing or logic
5. Show expected output/behavior
6. Be PBI-specific

### Example Template:
```
Example / Illustration only — values are not source-verified:

[Concrete scenario with specific data]
POD 'CNP_POD_12345' has best_forecast_id = 98765 in the pod_header table.
The forecast_model table has forecast_id = 98765 with last_forecasted_date = '2026-08-10T14:35:22.000Z'.

[Processing]
When the POD Details page loads, the backend queries these tables and returns the timestamp.

[Output]
The Last Forecasted Date column displays '08/10/2026 2:35:22 PM CDT' (for Central Time user).

[Note: Pod ID, forecast ID, and timestamps are illustrative examples only]
```

### What NOT to Do:
- ❌ Present fake data as actual system data
- ❌ Skip the example
- ❌ Use only generic descriptions
- ❌ Copy examples from other PBIs

---

## VISUAL FORMATTING DETAILS

### Colors (RGB)
- **Title**: RGB(0, 51, 102) - Dark blue
- **Heading 1**: RGB(54, 95, 145) - Medium blue
- **Heading 2**: RGB(79, 129, 189) - Light blue
- **Heading 3**: RGB(79, 129, 189) - Light blue
- **Feature subtitle**: RGB(0, 102, 204) - Blue
- **Body text**: Black

### Fonts and Sizes
- **Title**: Calibri 26pt, bold, center
- **Feature subtitle**: Calibri 14pt, bold, center
- **PBI metadata**: Calibri 10pt, center
- **Heading 1**: Calibri 14pt, bold
- **Heading 2**: Calibri 13pt, bold
- **Heading 3**: Calibri 11pt, bold
- **Body**: Calibri 11pt, normal

### Spacing
- **Title space after**: 12pt
- **Heading 1 space before**: 12pt, space after: 6pt
- **Heading 2 space before**: 10pt, space after: 4pt
- **Heading 3 space before**: 8pt, space after: 3pt
- **Paragraph space after**: 6pt
- **Line spacing**: 1.15

### Page Setup
- **Margins**: 1 inch (2.54cm) all sides
- **Page size**: Letter (8.5" x 11")
- **Orientation**: Portrait

---

## ANTI-HALLUCINATION RULES

### Information Priority (Highest to Lowest)
1. **PBI Description and Acceptance Criteria** = Highest priority source
2. **PBI Comments and Developer Notes** = Source
3. **PBI-Linked Integration Documentation** = Source
4. **PBI-Related Code** = Source (if accessible)
5. **Other PBIs** = Quality reference ONLY (never copy content)
6. **Generic Assumptions** = NOT acceptable as facts

### When Information is Missing:

**For Technical Details (table names, field names, queries)**:
```
[UNKNOWN - REQUIRES VERIFICATION]
or
[INFERRED - Database table/field names are not documented - verify actual implementation]
```

**For Business Logic**:
```
[INTERPRETATION - MEDIUM CONFIDENCE]
[Explain the logical interpretation, then note it needs verification]
```

**For Examples**:
```
Example / Illustration only — values are not source-verified:
[Provide illustrative example]
[Note: Values are examples only, not actual system data]
```

### Never Do:
- ❌ Invent API endpoints
- ❌ Invent database table names
- ❌ Invent field names
- ❌ Invent SQL queries
- ❌ Invent request/response payloads
- ❌ Invent business rules
- ❌ Invent test data and present it as real
- ❌ Copy technical details from another PBI

---

## QUALITY CHECKLIST

Before finalizing any document, verify:

### Structure
- ✓ Title page with correct formatting
- ✓ Section 1: Feature Overview (User Story, Background, Business Value, Scope)
- ✓ Section 2: AC Breakdown with ALL ACs

### Every AC Has:
- ✓ AC heading with proper formatting
- ✓ Given-When-Then or AC text
- ✓ QA Interpretation (detailed, PBI-specific)
- ✓ Example (concrete, with disclaimer if needed)
- ✓ Correct order (AC → QA Interpretation → Example)

### Content Quality:
- ✓ No content copied from other PBIs
- ✓ PBI-specific details only
- ✓ Technical details marked with confidence level
- ✓ Examples marked as illustrative if not source-verified
- ✓ No hallucinated table/field/API names
- ✓ Business values marked as INFERRED if not explicit

### Visual Formatting:
- ✓ Heading colors match template (dark/medium/light blue)
- ✓ Font sizes match template
- ✓ Spacing matches template
- ✓ Tables formatted correctly
- ✓ No text cutoff or overlap
- ✓ Clean page breaks
- ✓ Professional appearance

---

## EXAMPLE COMPARISON

### ❌ WRONG (Generic, Hallucinated):
```
AC-1: Display Last Forecasted Date

Given a POD exists
When user views POD Details
Then last forecast date is shown

QA Interpretation: Verify that the system correctly displays the last forecasted date.

Example: POD 12345 shows date "01/01/2026".
```

**Problems**:
- Generic QA interpretation
- No technical details
- No confidence marking
- Example has no context or processing details
- Appears to be real data (POD 12345) without disclaimer

### ✅ CORRECT (Detailed, Transparent):
```
AC-1: Display Last Forecasted Date from Best Forecast

Given a POD has an associated Best Forecast (best_forecast_id is populated in pod_header table)
When the POD Details page is loaded
Then the POD Details table shall display the Last Forecasted Date retrieved from the Best Forecast

QA Interpretation: [SOURCE-BACKED WHERE AVAILABLE] The backend must query pod_header.best_forecast_id to identify the Best Forecast, then retrieve forecast_model.last_forecasted_date for that forecast_id. The GET /pod-details/{pod} API response must include this timestamp in ISO 8601 format. The frontend must display it in the POD Details table. [Note: Table/field names are inferred from typical database schema - verify actual implementation]

Example / Illustration only — values are not source-verified:

POD 'CNP_POD_12345' has best_forecast_id = 98765 in the pod_header table. The forecast_model table has forecast_id = 98765 with last_forecasted_date = '2026-08-10T14:35:22.000Z'. When the POD Details page loads, the backend queries these tables and returns the timestamp. The Last Forecasted Date column displays '08/10/2026 2:35:22 PM CDT' (for Central Time user).

[Note: Pod ID, forecast ID, and timestamps are illustrative examples only]
```

**Correct because**:
- ✅ Detailed Given-When-Then
- ✅ Technical details with confidence marking
- ✅ Specific data sources mentioned (with verification note)
- ✅ Concrete example with full scenario
- ✅ Clear disclaimer that values are illustrative
- ✅ Shows input → processing → output

---

## FILE LOCATIONS

### Generated Documents
```
outputs/<PBI_NUMBER>/deliverables/QA_Understanding_Document_PBI_<NUMBER>.docx
```

**Example**:
```
outputs/645352/deliverables/QA_Understanding_Document_PBI_645352.docx
outputs/643243/deliverables/QA_Understanding_Document_PBI_643243.docx
```

### Generator
```
final_10_section_generator.py (permanent generator)
```

**Previous versions backed up as**:
```
final_10_section_generator.py.backup
final_10_section_generator.py.previous
```

### Template Reference
```
outputs/645352/deliverables/QA_Understanding_Document.docx (original template)
```

---

## USAGE

### Command
```bash
python scripts/final_10_section_generator.py <PBI_NUMBER>
```

### Example
```bash
python scripts/final_10_section_generator.py 650000
```

### What Happens
1. Loads `outputs/<PBI>/working/pbi-data.json`
2. Loads `outputs/<PBI>/working/integration-docs.json`
3. Splits concatenated ACs if needed
4. Generates document matching reference template
5. Applies exact visual formatting
6. Creates PBI-specific content with quality matching references
7. Marks unverified information appropriately
8. Saves to `outputs/<PBI>/deliverables/QA_Understanding_Document_PBI_<NUMBER>.docx`

---

## FOR ALL FUTURE PBIs

### Always:
- ✅ Use reference template visual style (colors, fonts, spacing)
- ✅ Match quality level of reference PBIs (detail, depth, examples)
- ✅ Include Given-When-Then for every AC
- ✅ Include detailed QA Interpretation for every AC
- ✅ Include concrete Example for every AC
- ✅ Mark confidence level for technical details
- ✅ Mark examples as illustrative if not source-verified
- ✅ Generate PBI-specific content only
- ✅ Maintain AC → QA Interpretation → Example order

### Never:
- ❌ Change template colors, fonts, or formatting
- ❌ Simplify or skip sections
- ❌ Remove QA Interpretations
- ❌ Remove Examples
- ❌ Copy content from other PBIs
- ❌ Hallucinate technical details
- ❌ Present assumptions as facts
- ❌ Change this standard automatically

---

## SUMMARY

**Template Source**: `outputs/645352/deliverables/QA_Understanding_Document.docx`
**Quality References**: PBI 645352, PBI 643243 (both GOOD examples)
**Generator**: `final_10_section_generator.py` (permanent)

**Standard**:
- Same visual formatting as template
- Same quality level as reference PBIs
- PBI-specific content only
- Detailed QA interpretations
- Concrete examples with disclaimers
- Confidence marking for all technical details
- Zero hallucination of unverified information

**This standard is LOCKED and will NOT change unless you explicitly request it.**

---

**Created**: 2026-08-27
**Status**: PERMANENT STANDARD
**Do Not Modify**: Without explicit user request