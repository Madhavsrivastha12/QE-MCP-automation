---
name: orchestrator-ng
description: "Use when invoking, debugging, or exploring the Orchestrator NG API (orchestrator-ng). Covers all endpoints: /resolve, /schedule, /purge, /ct-status. Includes curl examples with authentication for Dev, QA/Stage, Prelive/UAT environments. Token generation via MCP generate_identity_token or gcloud; requests always go to Load Balancer URL with Host: orchestrator-ng header."
---

# Orchestrator NG API

Task orchestration service (Go/Fiber) that manages multi-step pod forecast workflows via Cloud Tasks queues.

---

## Environments

| Environment | Load Balancer URL (use for requests) | Cloud Run URL (use for token only) |
|---|---|---|
| **Dev** | `https://10.69.56.26` | `https://orchestrator-ng-66911003298.us-central1.run.app` |
| **Stage/QA** | `https://10.69.59.100` | `https://orchestrator-ng-126612701852.us-central1.run.app` |
| **Prelive/UAT** | `https://10.69.59.150` | `https://orchestrator-ng-438706971075.us-central1.run.app` |

> **CRITICAL rules:**
> - Always generate the auth token using the **Cloud Run URL** as the audience.
> - Always send API requests to the **Load Balancer URL**.
> - Always include the header `Host: orchestrator-ng` on every request.

---

## Authentication

Use the MCP tool `generate_identity_token` with the Cloud Run URL as `audience`:

```
generate_identity_token(audience="https://orchestrator-ng-66911003298.us-central1.run.app")
```

The tool returns `{ "token": "<id-token>", "audience": "..." }`. Use the `token` value as the `Authorization: Bearer` header.

| Environment | Audience for `generate_identity_token` |
|---|---|
| Dev | `https://orchestrator-ng-66911003298.us-central1.run.app` |
| Stage/QA | `https://orchestrator-ng-126612701852.us-central1.run.app` |
| Prelive/UAT | `https://orchestrator-ng-438706971075.us-central1.run.app` |

Alternatively, generate a token via CLI (if MCP is unavailable):

```bash
TOKEN=$(gcloud auth print-identity-token --audiences="<Cloud Run URL>")
```

---

## Endpoints

### POST /resolve

Evaluates a task's result and dispatches the next step(s) to HTTP Cloud Task queues. Handles dependency failure propagation and parallel model steps.

**Request body — `TaskPayload`:**

| Field | Type | Description |
|---|---|---|
| `pod` | string | POD identifier |
| `podid` | int | POD numeric ID |
| `rawid` | int | Raw data ID |
| `dc` | string | Delivery channel |
| `source_type` | string | Source type (optional) |
| `yeartype` | string | Year type (optional) |
| `force_reprocess` | bool | Force reprocessing flag |
| `steps` | string[] | Remaining steps to execute |
| `task_id` | string | Current task ID |
| `session_id` | string | Forecast session ID |
| `graph_id` | string | Execution graph ID |
| `task_id_namespace` | string | Namespace for task ID tracking |
| `result.current_step` | string | Step that just completed |
| `result.is_success` | bool | Whether the completed step succeeded |
| `result.custom_dep_failure` | string | Custom failure status label (optional) |

**curl — Dev:**
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://orchestrator-ng-66911003298.us-central1.run.app")

curl -k -s -X POST "https://10.69.56.26/resolve" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pod": "EXAMPLE_POD",
    "podid": 12345,
    "rawid": 67890,
    "dc": "ERCOT",
    "steps": ["scalar", "publish"],
    "task_id": "task-uuid-here",
    "session_id": "session-uuid-here",
    "graph_id": "graph-uuid-here",
    "task_id_namespace": "namespace-here",
    "result": {
      "current_step": "idr-contseason",
      "is_success": true,
      "custom_dep_failure": ""
    }
  }'
```

**curl — Stage/QA:**
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://orchestrator-ng-126612701852.us-central1.run.app")

curl -k -s -X POST "https://10.69.59.100/resolve" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

**curl — Prelive/UAT:**
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://orchestrator-ng-438706971075.us-central1.run.app")

curl -k -s -X POST "https://10.69.59.150/resolve" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

---

### POST /schedule

Reads a row group from a GCS Parquet object, schedules each task payload into Cloud Tasks, and optionally enqueues the next row group.

**Request body — `TaskInject`:**

| Field | Type | Description |
|---|---|---|
| `bucket` | string | GCS bucket name |
| `object` | string | GCS object path (parquet file) |
| `row_group` | int | Row group index within the parquet file |
| `session_id` | string | Forecast session ID |

**curl — Dev:**
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://orchestrator-ng-66911003298.us-central1.run.app")

curl -k -s -X POST "https://10.69.56.26/schedule" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bucket": "prj-nrg-dev-bucket-ue",
    "object": "sessions/my-session/tasks.parquet",
    "row_group": 0,
    "session_id": "session-uuid-here"
  }'
```

**curl — Stage/QA:**
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://orchestrator-ng-126612701852.us-central1.run.app")

curl -k -s -X POST "https://10.69.59.100/schedule" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

**curl — Prelive/UAT:**
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://orchestrator-ng-438706971075.us-central1.run.app")

curl -k -s -X POST "https://10.69.59.150/schedule" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

---

### POST /purge

Purges (deletes) specific task IDs from a Cloud Tasks queue.

**Request body — `PurgePayload`:**

| Field | Type | Description |
|---|---|---|
| `queue` | string | Cloud Tasks queue name |
| `task_ids` | string[] | List of task IDs to purge |

**curl — Dev:**
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://orchestrator-ng-66911003298.us-central1.run.app")

curl -k -s -X POST "https://10.69.56.26/purge" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "queue": "my-queue-name",
    "task_ids": ["task-id-1", "task-id-2"]
  }'
```

**curl — Stage/QA:**
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://orchestrator-ng-126612701852.us-central1.run.app")

curl -k -s -X POST "https://10.69.59.100/purge" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

**curl — Prelive/UAT:**
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://orchestrator-ng-438706971075.us-central1.run.app")

curl -k -s -X POST "https://10.69.59.150/purge" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

---

### POST /ct-status

Retrieves the status of a Cloud Tasks task by task ID and queue name.

**Request body — `CTInfoRequest`:**

| Field | Type | Description |
|---|---|---|
| `task_id` | string | The Cloud Tasks task ID |
| `queue` | string | The Cloud Tasks queue name |

**Response — `CTInfo`:**

| Field | Type | Description |
|---|---|---|
| `name` | string | Full task resource name |
| `create_time` | string (ISO8601) | When the task was created |
| `dispatch_count` | int | Number of dispatch attempts |
| `first_attempt` | string (ISO8601) | Timestamp of first attempt |
| `last_attempt` | string (ISO8601) | Timestamp of most recent attempt |

**curl — Dev:**
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://orchestrator-ng-66911003298.us-central1.run.app")

curl -k -s -X POST "https://10.69.56.26/ct-status" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "my-task-id",
    "queue": "my-queue-name"
  }'
```

**curl — Stage/QA:**
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://orchestrator-ng-126612701852.us-central1.run.app")

curl -k -s -X POST "https://10.69.59.100/ct-status" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

**curl — Prelive/UAT:**
```bash
TOKEN=$(gcloud auth print-identity-token --audiences="https://orchestrator-ng-438706971075.us-central1.run.app")

curl -k -s -X POST "https://10.69.59.150/ct-status" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

---

## Common Errors

| Status | Meaning |
|---|---|
| 400 | Bad request — malformed JSON or missing required fields |
| 500 | Internal error — GCS read failure, DB error, or Cloud Tasks error |
| 401/403 | Auth token invalid, expired, or wrong audience |

> Tokens expire after ~1 hour. Call `generate_identity_token` again or re-run the `gcloud` command to refresh.

---

## Quick Reference: Token + URL by Environment

```
# ── Dev ─────────────────────────────────────────────────────────────
LB_URL  = https://10.69.56.26
CR_URL  = https://orchestrator-ng-66911003298.us-central1.run.app

# ── Stage/QA ────────────────────────────────────────────────────────
LB_URL  = https://10.69.59.100
CR_URL  = https://orchestrator-ng-126612701852.us-central1.run.app

# ── Prelive/UAT ─────────────────────────────────────────────────────
LB_URL  = https://10.69.59.150
CR_URL  = https://orchestrator-ng-438706971075.us-central1.run.app
```

**Token (via MCP):**
```
generate_identity_token(audience="<CR_URL>")  →  { "token": "...", "audience": "..." }
```

**Request pattern:**
```bash
curl -k -s -X POST "<LB_URL>/<endpoint>" \
  -H "Host: orchestrator-ng" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```
