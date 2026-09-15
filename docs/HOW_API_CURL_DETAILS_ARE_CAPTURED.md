# How API/curl Details Are Captured in the QA Agent System

> **Updated 2026-09-11.** Phase 2 no longer scans `docs/integrations/`. It reads
> **only** the files you explicitly provide in Phase 1. Sections below marked
> *(updated)* reflect the current behaviour. The same mechanism now applies to
> UI, Database, Business Logic, and Integration testing — not just API.

## Overview

The system captures API/curl details through a **two-source approach**:
1. **User Input** during Phase 1 (interactive collection)
2. **Supporting documentation MD files that you provide by path** in Phase 1,
   parsed in Phase 2

Both sources are optional in the sense that either can be empty — but if
neither supplies a detail, the agents **record it as an open question rather
than inventing it**.

---

## Source 1: User Input During Phase 1

### When the Workflow Starts

When you run `@qa-workflow <PBI_NUMBER>`, the orchestrator asks you questions:

#### Step 1: Select Test Type
```
Question: What type of testing are you performing?
Options:
  - API/Endpoint Testing
  - UI/Frontend Testing
  - Database Testing
  - Mixed Testing (select multiple)
```

#### Step 2: Provide API Endpoint (if API selected)
```
Question: Which API/endpoint are you testing?
Example: POST /pod-forecast-batch-results
```

You provide: `POST /pod-forecast-batch-results`

#### Step 3: Iterative Information Collection Loop

After you provide the endpoint, the agent asks:

```
"Would you like to add more information? 

You can provide:
- Request details (headers, body, parameters)
- Expected behavior
- Business rules
- Test data requirements
- Any other relevant context

Please share any additional information, or respond with 'No, that's all' when done."
```

### What You Can Provide

You can provide curl details in plain text, and the agent will capture them:

**Example 1: Provide curl command directly**
```bash
curl -X POST https://api.example.com/pod-forecast-batch-results \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "pods": [
      {"pod": "POD123", "dc": "CNP"}
    ],
    "startdate": "07/01/2026",
    "enddate": "07/31/2026",
    "return_meterload": true
  }'
```

**Example 2: Provide request details in structured text**
```
Request headers:
- Authorization: Bearer token from identity endpoint
- Content-Type: application/json

Request body:
{
  "pods": [{"pod": "POD123", "dc": "CNP"}],
  "startdate": "07/01/2026",
  "enddate": "07/31/2026",
  "return_meterload": true
}

Expected response: 200 OK with forecast results
```

**Example 3: Provide business rules**
```
Business rules:
- startdate and enddate must be provided together
- enddate must be >= startdate
- At least one load type flag must be true
- Date format: MM/DD/YYYY
```

### How It's Stored

All this information is saved to `user-context.json`:

```json
{
  "pbi_number": "643243",
  "selected_types": ["API"],
  "primary_type": "API",
  "components": {
    "API": "POST /pod-forecast-batch-results"
  },
  "details": {
    "api_endpoint": "POST /pod-forecast-batch-results"
  },
  "additional_information": [
    "curl -X POST https://api.example.com/pod-forecast-batch-results...",
    "Request headers: Authorization: Bearer token...",
    "Business rules: startdate and enddate must be provided together..."
  ],
  "collected_at": "2026-09-08T14:00:00"
}
```

---

## Source 2: Supporting Documentation You Provide *(updated)*

### Step 2.1d — You Are Asked for File Paths

After you select your test type(s) and component(s), Phase 1 asks:

```
Please provide the relevant supporting documentation file path(s) for the
selected testing type(s). You can provide one file that covers multiple types
or separate files. If no documentation is available, enter none.
```

- One path per line; a single file may cover several types.
- Answer `none` (also `no`, `n/a`, `skip`, or blank) to continue without any.
- **The agent does not go looking.** If you provide nothing, nothing is read —
  it will not fall back to `docs/integrations/`.
- A bad path is reported back to you and re-asked; it is never silently skipped
  and never swapped for a different file.

The result is stored in `user-context.json`:

```json
{
  "documents_provided": true,
  "provided_documents": [
    {"path": "C:/specs/pod-forecast-batch-results.md",
     "as_entered": "docs/integrations/apis/pod-forecast-batch-results.md",
     "exists": true, "size_bytes": 8432}
  ]
}
```

`docs/integrations/apis/pod-forecast-batch-results.md` still exists in the repo
and is a perfectly good file to point at — you just have to point at it.

### How Agents Read This Documentation *(updated)*

During **Phase 2**, the `md-file-reader` agent:

1. Reads **only** the files listed in `provided_documents` (no directory scan;
   the agent is not even granted the Glob tool)
2. Parses the documentation structure
3. Extracts — **only for the types in `selected_types`**:
   - HTTP method (GET, POST, PUT, DELETE)
   - Endpoint path
   - Path parameters
   - Query parameters
   - Request body schema
   - Response schema
   - Error scenarios
   - Example curl commands
   - Authentication requirements

4. Saves everything to `integration-docs.json`:

```json
{
  "apis": [
    {
      "file": "pod-forecast-batch-results.md",
      "endpoint": "/pod-forecast-batch-results",
      "method": "POST",
      "description": "Retrieves forecast results for multiple PODs...",
      "request_body": {
        "pods": "List[PodDcPair]",
        "startdate": "date (MM/DD/YYYY)",
        "enddate": "date (MM/DD/YYYY)",
        "return_meterload": "boolean (default: true)"
      },
      "response": {
        "status": "SUCCESS/ERROR",
        "data": "list[dict] - forecast results grouped by POD"
      },
      "validation_rules": [
        "pods list must contain at least 1 item",
        "Both startdate and enddate must be provided together",
        "enddate must be >= startdate"
      ],
      "error_scenarios": [
        "400: Missing one date parameter",
        "400: enddate < startdate",
        "422: Empty PODs list"
      ],
      "example_curl": "curl -X POST /pod-forecast-batch-results..."
    }
  ],
  "database": [],
  "businessLogic": [],
  "ui": [],
  "integration": [],
  "scope": {"selected_types": ["API"]},
  "documents_provided": true,
  "extraction_gaps": [],
  "out_of_scope_content_seen": [],
  "metadata": {"sourceMode": "user-provided (no project scan)"}
}
```

**Note the five buckets.** The mechanism is generic — a UI-only run fills `ui`
and leaves the rest empty, exactly as an API-only run fills `apis`.

### Scope Is Decided Before Any Document Is Read

`selected_types` is frozen when you answer the test-type question, **before**
the documentation question is asked. Document contents can never add, remove,
or change a test type:

- Provide an API spec during a UI-only run → the API content is **discarded**
  and logged under `out_of_scope_content_seen`. No API tests appear.
- Provide a file covering API + DB but select only API → only API is extracted.

### When a Selected Type Has No Documentation

Each selected type with an empty bucket produces an `extraction_gaps` entry:

```json
"extraction_gaps": [
  {"type": "Database", "reason": "provided documentation contained no content for this type"}
]
```

Phase 3 renders every gap as an **Open Question** in the QA Understanding
Document. The gap stays visible instead of being filled with a plausible guess.

---

## How Both Sources Combine in Phase 3

During **Phase 3**, the `qa-understanding-doc-creator` agent creates the QA Understanding Document by:

1. **Loading user-context.json** (what you provided)
2. **Loading integration-docs.json** (pre-written API specs)
3. **Loading pbi-data.json** (PBI from Azure DevOps)

Then it **merges** all three sources:

### Section 3: API Endpoint Details (from integration docs)
- HTTP Method: POST
- Path: /pod-forecast-batch-results
- Request parameters (from MD file)
- Response schema (from MD file)

### Section 4: Request/Response Examples (from integration docs)
- Example curl commands (from MD file)
- Sample request body (from MD file)
- Sample response (from MD file)

### Section 5: Validation Rules (from integration docs)
- Date pairing validation (from MD file)
- Date range validation (from MD file)

### Section 6: Error Scenarios (from integration docs)
- 400 errors (from MD file)
- 422 errors (from MD file)

### Section 7: Business Rules (from user input + integration docs)
- Rules from MD file
- **Additional rules you provided** during Phase 1

### Section 8: QA Test Interpretation
- Uses ALL information to generate test scenarios
- Combines PBI acceptance criteria + API specs + your input

---

## The Two-Source Strategy

| Information | Source | When Captured |
|-------------|--------|---------------|
| **API endpoint name** | User input (Phase 1) | `@qa-workflow` start |
| **Additional context** | User input (Phase 1) | Iterative loop |
| **Documentation file paths** | User input (Phase 1) | Step 2.1d |
| **curl commands** | User input OR provided docs | Phase 1 OR Phase 2 |
| **Request schema** | Provided docs (Phase 2) | MD file parsing |
| **Response schema** | Provided docs (Phase 2) | MD file parsing |
| **Validation rules** | Provided docs (Phase 2) | MD file parsing |
| **Error scenarios** | Provided docs (Phase 2) | MD file parsing |
| **Authentication** | Provided docs (Phase 2) | MD file parsing |
| **Anything none of the above supplies** | **Open Question, not invented** | Phase 3 |

---

## Example Workflow: How curl Details Flow

### Scenario: Testing POST /pod-forecast-batch-results

#### Phase 1: User Input
```
@qa-workflow 643243

Agent: "What type of testing?"
You: "API/Endpoint Testing"

Agent: "Which API/endpoint are you testing?"
You: "POST /pod-forecast-batch-results"

Agent: "Would you like to add more information?"
You: "Yes, here's the curl command:
     curl -X POST https://dev-api.example.com/pod-forecast-batch-results \
       -H 'Authorization: Bearer <token>' \
       -d '{"pods": [{"pod": "POD123", "dc": "CNP"}], "startdate": "07/01/2026"}'
     "

Agent: "Would you like to add more information?"
You: "Yes, the token comes from GET /identity/token"

Agent: "Would you like to add more information?"
You: "No, that's all."

Agent: "Please provide the relevant supporting documentation file path(s) for
        the selected testing type(s). You can provide one file that covers
        multiple types or separate files. If no documentation is available,
        enter none."
You: "docs/integrations/apis/pod-forecast-batch-results.md"

✅ Saved to: user-context.json
   documents_provided: true
   provided_documents: [ .../pod-forecast-batch-results.md ]
```

#### Phase 2: Reading the Documents You Provided
```
Agent reads ONLY: docs/integrations/apis/pod-forecast-batch-results.md
                  (because you listed it — no directory was scanned)

Extracts (API only, since selected_types = ["API"]):
- Complete request schema
- All validation rules
- Error scenarios
- Response format
- Example curl commands
- Authentication details

✅ Saved to: integration-docs.json
```

#### Phase 3: QA Understanding Document
```
Agent creates: QA_Understanding_Document.docx

Combines:
- PBI acceptance criteria
- Your curl command (from user-context.json)
- Complete API spec (from integration-docs.json)
- Your token note (from user-context.json)

Result:
Section 3: API Endpoint Details
  - HTTP Method: POST
  - Path: /pod-forecast-batch-results
  - Request schema (from integration-docs.json)

Section 4: Authentication
  - Bearer token required
  - Token source: GET /identity/token (from user-context.json)

Section 5: Example Request
  - curl command (from user-context.json OR integration-docs.json)

Section 7: Business Rules
  - All validation rules (from integration-docs.json)
  - Any additional rules you mentioned
```

---

## What If You Have No Documentation? *(updated)*

Answer `none`. This is a fully supported path, not a degraded one.

### The Agent Relies on User Input Only

Phase 2 still writes `integration-docs.json` — with empty buckets,
`documents_provided: false`, and one `extraction_gaps` entry per selected type —
so Phase 3 does not fail merely because you had no document:
```
ℹ️  No supporting documents were provided.
    Building from PBI data + your additional information only.
    1 selected type(s) recorded as gaps.
```

Phase 3 will:
- Use whatever you provided in Phase 1
- Generate test scenarios based on:
  - PBI acceptance criteria
  - Your curl command
  - Your business rules
  - Your additional context

### You Should Provide More Details

If the MD file doesn't exist, provide more during Phase 1:

```
Agent: "Would you like to add more information?"
You: "Yes, here's the complete request schema:
     Request body:
     - pods: array of {pod, dc} objects (required, min 1)
     - startdate: MM/DD/YYYY format (optional, but if provided, enddate required)
     - enddate: MM/DD/YYYY format (optional, but if provided, startdate required)
     - return_meterload: boolean (default true)
     
     Validation:
     - enddate must be >= startdate
     - At least one return_* flag must be true
     
     Response: 200 OK with {status: 'SUCCESS', data: [...]}
     
     Errors:
     - 400: Both startdate and enddate must be provided together
     - 400: enddate < startdate
     - 422: Empty pods list
     "
```

The agent will capture all of this in `user-context.json` and use it in Phase 3.

---

## Best Practices

### ✅ DO

1. **Provide the endpoint name** in Phase 1
   - Example: `POST /pod-forecast-batch-results`

2. **Provide curl commands** if you have them
   - Full curl with headers, body, auth

3. **Provide business rules** specific to this PBI
   - Any rules not already in integration docs

4. **Maintain reusable docs** in `docs/integrations/apis/` (or anywhere)
   - Keeps specs consistent across PBIs and reduces retyping
   - **Then point at them by path** at the Step 2.1d prompt — the agent will not
     find them on its own

5. **Answer `none` honestly** when you have no document
   - A thin, accurate document beats a full, invented one
   - Read the Open Questions section afterwards; it tells you exactly what to
     supply next run

### ❌ DON'T

1. **Don't skip Phase 1 questions**
   - The agent needs at least the endpoint name

2. **Don't assume the agent has curl details**
   - Provide them if integration docs don't exist

3. **Don't hardcode secrets in curl commands**
   - Use placeholders: `<token>`, `<api-key>`

---

## Summary

**How curl details are captured:**

1. **User provides** during Phase 1 iterative loop:
   - API endpoint name (required)
   - curl commands (optional, if available)
   - Business rules (optional, additional context)

2. **The documents you pointed at** are parsed during Phase 2:
   - Complete API specification
   - Request/response schemas
   - Validation rules
   - Error scenarios
   - Example curl commands
   - (and the UI / DB / Business Logic / Integration equivalents, for those types)

3. **Phase 3 merges the three permitted sources**:
   - PBI data, your provided documentation, your additional information
   - User input takes precedence for PBI-specific details
   - Anything none of them supplies becomes an **Open Question**

**Result**: complete testing documentation without retyping everything — and,
where a detail genuinely isn't available, an explicit gap instead of a
convincing guess.

---

## Files to Check

| File | Purpose |
|------|---------|
| `user-context.json` | Your input from Phase 1, incl. `provided_documents` |
| `integration-docs.json` | Parsed provided documents + `extraction_gaps` |
| `QA_Understanding_Document.docx` | Final merged document, incl. Open Questions |
| `docs/integrations/apis/*.md` | Reusable specs — **provide the path to use them** |

---

**Last Updated**: 2026-09-11
