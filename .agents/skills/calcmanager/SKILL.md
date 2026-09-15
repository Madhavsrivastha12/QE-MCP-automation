---
name: calcmanager
description: "Use when submitting pod forecast jobs via the Calcmanager API (/submit-ng). Covers authentication, Pod request body, X-Force-Reprocess and X-Active-Step headers, MCP tools for source_type lookup and session monitoring, and curl examples for Dev, Stage/QA, and Prelive/UAT environments."
---

# Calcmanager API

Calcmanager builds and dispatches pod forecast task graphs. The `/submit-ng` endpoint is the **only supported path** — `/submit` is deprecated and must not be used.

---

## Environments

| Environment | Load Balancer URL (use for requests) | Cloud Run URL (use for token only) |
|---|---|---|
| **Dev** | `https://10.69.56.26` | `https://calcmanager-66911003298.us-central1.run.app` |
| **Stage/QA** | `https://10.69.59.100` | `https://calcmanager-126612701852.us-central1.run.app` |
| **Prelive/UAT** | `https://10.69.59.150` | `https://calcmanager-438706971075.us-central1.run.app` |

> **CRITICAL rules:**
> - Always generate the auth token using the **Cloud Run URL** as the audience.
> - Always send API requests to the **Load Balancer URL**.
> - Always include the header `Host: calcmanager-service` on every request.
> - If not already specified in the user's request, always explicitly ask the user whether they want to force a reprocess (using the `X-Force-Reprocess: 1` header) before submitting the forecast job. If using Claude, always use the `ask_question` tool (also known as `AskUserQuestion` in some client environments) to present this and any other options to the user rather than asking via plain text.
> - **Always stop the forecast flow after retrieving and presenting the completion status of the session ID.** Always present the session results directly in the main chat response to the user as a detailed table listing all tasks, their statuses, start/end times, and any associated error details (do not hide them inside an external report or artifact file). The user will review the details and ask further questions. **Do not attempt to debug any forecast errors or task failures yourself unless explicitly asked by the user.**


---

## Useful MCP Tools

These tools are available in the Usage Empire MCP server (`ue-api/src/mcp/server.py`) and are useful when working with calcmanager.

### `get_source_type(pod)`

Looks up the `source_type` for a pod from the `edi_site` table and returns it already formatted for use in a calcmanager payload.

```
get_source_type(pod="EXAMPLE_POD")
→ { "pod": "EXAMPLE_POD", "source": "EDI", "source_type": "VHOS-EDI" }
```

Use the `source_type` field directly in the `/submit-ng` request body. If no row is found, returns `{ "error": "..." }`.

### `get_session_status(session_id)`

Monitors the progress of a running or completed calcmanager job by querying `calc_status`.

```
get_session_status(session_id="<uuid returned by /submit-ng>")
→ [ { ...all calc_status columns... }, ... ]
```

Call this after `/submit-ng` returns a `session_id` to track task-level progress. Returns an error object if the session ID is not found.

---

## Authentication

Use the MCP tool `generate_identity_token` with the Cloud Run URL as `audience`:

```
generate_identity_token(audience="https://calcmanager-66911003298.us-central1.run.app")
```

Returns `{ "token": "<id-token>", "audience": "..." }`. Use `token` as the `Authorization: Bearer` value.

| Environment | Audience for `generate_identity_token` |
|---|---|
| Dev | `https://calcmanager-66911003298.us-central1.run.app` |
| Stage/QA | `https://calcmanager-126612701852.us-central1.run.app` |
| Prelive/UAT | `https://calcmanager-438706971075.us-central1.run.app` |

Fallback (CLI):
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="<Cloud Run URL>")
```

---

## POST /submit-ng

Builds the forecast task graph for the given pods, writes it as a Parquet file to GCS, and triggers orchestrator-ng `/schedule` to begin execution. Returns immediately with a `session_id`.

### Required headers

| Header | Required | Description |
|---|---|---|
| `Authorization` | yes | `Bearer <id-token>` |
| `Host` | yes | Must be `calcmanager-service` |
| `userId` | yes | Identifies the user submitting the job (e.g. `jsmith`) |
| `Content-Type` | yes | `application/json` |

### Optional headers

See detailed sections below for `X-Force-Reprocess` and `X-Active-Step`.

### Request body

Array of `Pod` objects:

| Field | Type | Required | Description |
|---|---|---|---|
| `pod` | string | one of `pod`/`podid` | POD name |
| `dc` | string | required when `pod` is set | Distribution company / delivery channel |
| `podid` | int | one of `pod`/`podid` | POD numeric ID (resolves `pod` and `dc` from DB) |
| `rawid` | int | no | Raw data ID (optional override) |
| `source_type` | string | conditional | Required when `raw-manager` is in scope (see below). Allowed values: `VHOS-EDI`, `VHOS-MDR`, `VHOS-IRW`, `VHOS-OTS` |

**Validation rules:**
- Either `pod` or `podid` must be provided (not both, not neither).
- If `pod` is provided, `dc` must also be provided.
- `source_type` is **required** when `X-Active-Step` is omitted (full run) or when `raw-manager` is explicitly listed in `X-Active-Step`.
- **Important Rule:** If `raw-manager` is NOT involved in the run (meaning `raw-manager` is omitted or excluded from the `X-Active-Step` header list), then `source_type` is **NOT** needed and can be omitted entirely.

### Response

```json
{ "session_id": "<uuid>" }
```

---

## Header: X-Force-Reprocess

Controls whether the orchestrator skips any cached / previously-completed state for tasks in this run.

| Value | Behaviour |
|---|---|
| `1` | Force reprocess — all steps are rerun even if they previously completed successfully |
| `0` (default) | Normal run — already-completed tasks are not repeated |

```bash
-H "X-Force-Reprocess: 1"
```

Use this when:
- A pod's source data was corrected and you need results to be recalculated from scratch.
- A prior session completed partially and stale results need to be overwritten.
- Debugging a specific step that cached an incorrect result.

> **Important Rule:** If the user request does not state whether to force reprocess, you must explicitly ask the user whether they want to force a reprocess or perform a normal cached run before submitting the request. If using Claude, always use the `ask_question` tool (also known as `AskUserQuestion` in some client environments) to present these options to the user rather than asking via plain text.

---

## Header: X-Active-Step

Restricts which pipeline steps are included in the task graph. When omitted, all steps are scheduled.

```bash
-H "X-Active-Step: scalar,publish"
```

Can also be sent as a single comma-separated value or as repeated headers — both are handled identically.

### Available steps

| Step | Description |
|---|---|
| `raw-manager` | Ingest raw interval data |
| `site-edi` | Site EDI processing |
| `pod-obligation` | POD obligation (auto-skipped for ERCOT-market pods) |
| `scalar` | Scalar forecast model |
| `idr-contseason` | IDR cont-season forecast |
| `idr-months` | IDR months forecast |
| `day-match` | Day-match forecast |
| `default` | Default forecast model |
| `model-selector` | Best-model selector |
| `load-growth` | Load growth model |
| `pod-status-manager` | POD status updates |
| `compute-lfp` | LFP computation (auto-skipped for non-ERCOT/PJM pods) |
| `publish` | Publish results |
| `site` | Site forecast |

Models `scalar`, `idr-contseason`, `idr-months`, `day-match`, `default` are also filtered by the `model_run_config` DB table — disabled models are silently dropped.

### Common `X-Active-Step` patterns

| Goal | Header value |
|---|---|
| Full pipeline (default) | *(omit header)* |
| Rerun forecasts only | `scalar,idr-contseason,idr-months,day-match,default` |
| Rerun and publish | `scalar,idr-contseason,idr-months,day-match,default,publish` |
| Publish only | `publish` |
| Raw ingest only | `raw-manager` |
| Raw + site EDI | `raw-manager,site-edi` |

> When `raw-manager` is in scope (explicit or via full run), `source_type` on every pod becomes **mandatory**.
> Conversely, if `raw-manager` is NOT involved in the run, `source_type` is **not required** and can be omitted.

---

## curl Examples

### Dev — full pipeline run

```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://calcmanager-66911003298.us-central1.run.app")

curl -k -s -X POST "https://10.69.56.26/submit-ng" \
  -H "Host: calcmanager-service" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "userId: jsmith" \
  -d '[
    {
      "pod": "EXAMPLE_POD",
      "dc": "ONCOR",
      "source_type": "VHOS-EDI"
    }
  ]'
```

### Dev — specific steps only (no raw ingest, no source_type needed)

```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://calcmanager-66911003298.us-central1.run.app")

curl -k -s -X POST "https://10.69.56.26/submit-ng" \
  -H "Host: calcmanager-service" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "userId: jsmith" \
  -H "X-Active-Step: scalar,idr-contseason,idr-months,day-match,default,publish" \
  -d '[
    { "pod": "EXAMPLE_POD", "dc": "ONCOR" }
  ]'
```

### Dev — force reprocess all steps

```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://calcmanager-66911003298.us-central1.run.app")

curl -k -s -X POST "https://10.69.56.26/submit-ng" \
  -H "Host: calcmanager-service" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "userId: jsmith" \
  -H "X-Force-Reprocess: 1" \
  -d '[
    { "pod": "EXAMPLE_POD", "dc": "ONCOR", "source_type": "VHOS-EDI" }
  ]'
```

### Dev — submit by podid

```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://calcmanager-66911003298.us-central1.run.app")

curl -k -s -X POST "https://10.69.56.26/submit-ng" \
  -H "Host: calcmanager-service" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "userId: jsmith" \
  -d '[
    { "podid": 12345, "source_type": "VHOS-MDR" }
  ]'
```

### Stage/QA

```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://calcmanager-126612701852.us-central1.run.app")

curl -k -s -X POST "https://10.69.59.100/submit-ng" \
  -H "Host: calcmanager-service" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "userId: jsmith" \
  -d '[ ... ]'
```

### Prelive/UAT

```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://calcmanager-438706971075.us-central1.run.app")

curl -k -s -X POST "https://10.69.59.150/submit-ng" \
  -H "Host: calcmanager-service" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "userId: jsmith" \
  -d '[ ... ]'
```

---

## Common Errors

| Status | Cause |
|---|---|
| 400 `userId not found in headers` | `userId` header missing |
| 400 `source_type must not be non-null or empty value` | `source_type` missing when `raw-manager` is in scope |
| 400 `either pod or podid must be set` | Pod body missing both `pod` and `podid` |
| 400 `dc cannot be null or empty` | `pod` supplied without `dc` |
| 401/403 | Token invalid, expired, or wrong audience |

---

## Quick Reference

```
# ── Dev ─────────────────────────────────────────────────────────────
LB_URL  = https://10.69.56.26
CR_URL  = https://calcmanager-66911003298.us-central1.run.app

# ── Stage/QA ────────────────────────────────────────────────────────
LB_URL  = https://10.69.59.100
CR_URL  = https://calcmanager-126612701852.us-central1.run.app

# ── Prelive/UAT ─────────────────────────────────────────────────────
LB_URL  = https://10.69.59.150
CR_URL  = https://calcmanager-438706971075.us-central1.run.app
```

**Token (via MCP):**
```
generate_identity_token(audience="<CR_URL>")  →  { "token": "...", "audience": "..." }
```

**Request pattern:**
```bash
curl -k -s -X POST "<LB_URL>/submit-ng" \
  -H "Host: calcmanager-service" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -H "userId: <user>" \
  [-H "X-Force-Reprocess: 1"] \
  [-H "X-Active-Step: <step1>,<step2>,..."] \
  -d '[ { "pod": "...", "dc": "...", "source_type": "..." } ]'
```
