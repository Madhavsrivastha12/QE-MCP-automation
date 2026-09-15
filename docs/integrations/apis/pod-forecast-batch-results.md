# Pod Forecast Results API Documentation

This document provides information about the Pod Forecast Results API endpoints that retrieve forecast data for PODs (Points of Delivery). These endpoints return hourly load data across different load types (meterload, genload, distributionload, ufeload, transmissionload).

## 1. GET /pod-forecast-results/{dc}/{pod}

### Description
Retrieves forecast results for a single POD (Point of Delivery) with optional date filtering and load type selection.

### HTTP Method
GET

### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| dc | string | Yes | Distribution Company identifier |
| pod | string | Yes | Point of Delivery identifier |

### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| startdate | date | No | None | Start date in MM/DD/YYYY format. Must be provided with enddate |
| enddate | date | No | None | End date in MM/DD/YYYY format. Must be provided with startdate |
| return_meterload | boolean | No | true | Include meter load columns in response |
| return_genload | boolean | No | false | Include generation load columns in response |
| return_distributionload | boolean | No | false | Include distribution load columns in response |
| return_ufeload | boolean | No | false | Include UFE load columns in response |
| return_transmissionload | boolean | No | false | Include transmission load columns in response |

### Request Validation
- Date Pairing: Both startdate and enddate must be provided together or omitted together
- Date Range: enddate must be greater than or equal to startdate

### Response
Type: UEResponse[list[dict]]

Success Response:
```json
{
  "status": "success",
  "data": [
    {
      "pod": "POD123",
      "dc": "CNP",
      "loadday": "2026-07-07",
      "meterload_h1": 0.004567890123456,
      "meterload_h2": 0.005123450987654,
      "meterload_h3": 0.004876543210987,
      "...": "...",
      "meterload_h25": 0.003987654321098,
      "genload_h1": 0.004432109876543,
      "genload_h2": 0.004987654321098,
      "...": "...",
      "genload_h25": 0.003765432109876
    }
  ]
}
```

Error Response (400 Bad Request):
```json
{
  "status": "ERROR",
  "message": "Both 'startdate' and 'enddate' must be provided together or omitted together."
}
```

### Response Fields
- status: Response status (SUCCESS/ERROR)
- data: Array of forecast records, each containing:
  - pod: POD identifier
  - dc: Delivery center code
  - loadday: Date in YYYY-MM-DD format
  - {load_type}_h{hour}: Load value for specific hour (h1 through h25)
    - Hours 1-24: Standard hours
    - Hour 25: DST transition support

### Processing Flow
1. Validates date parameters (must be paired, enddate >= startdate)
2. Constructs internal request with result_format: "podloadhour"
3. Calls get_batch_results() to fetch forecast data
4. Processes results via prepare_data_for_podloadhour_for_results()
5. Drops loadmonth and forecastid columns
6. Reorders columns: pod, dc, loadday first
7. Filters load type columns based on request flags (meterload_, genload_, etc.)
8. Formats loadday as YYYY-MM-DD
9. Returns JSON with double precision (15 decimal places)

### Example Usage
```bash
# Get all meter load for a POD in July 2026
GET /pod-forecast-results/CNP/POD123?startdate=07/01/2026&enddate=07/31/2026&return_meterload=true

# Get all load types for a POD (no date filter)
GET /pod-forecast-results/TNP/POD456?return_meterload=true&return_genload=true&return_distributionload=true&return_ufeload=true&return_transmissionload=true
```

---

## 2. POST /pod-forecast-results-aggregations

### Description
Retrieves forecast results for multiple PODs and aggregates them by loadday, summing all numeric columns across PODs.

### HTTP Method
POST

### Request Body
Type: BatchPodLoadRequest

```json
{
  "pods": [
    {"pod": "POD123", "dc": "CNP"},
    {"pod": "POD456", "dc": "TNP"}
  ],
  "startdate": "07/01/2026",
  "enddate": "07/31/2026",
  "return_meterload": true,
  "return_genload": false,
  "return_distributionload": false,
  "return_ufeload": false,
  "return_transmissionload": false
}
```

### Schema
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| pods | List[PodDcPair] | Yes | - | List of POD/DC pairs (minimum 1) |
| startdate | date | No | None | Start date in MM/DD/YYYY format |
| enddate | date | No | None | End date in MM/DD/YYYY format |
| return_meterload | boolean | No | true | Include meter load columns |
| return_genload | boolean | No | false | Include generation load columns |
| return_distributionload | boolean | No | false | Include distribution load columns |
| return_ufeload | boolean | No | false | Include UFE load columns |
| return_transmissionload | boolean | No | false | Include transmission load columns |

### Request Validation
- pods list must contain at least 1 item
- Both startdate and enddate must be provided together or omitted together
- enddate must be >= startdate

### Response
Type: UEResponse[list[dict]]

Success Response (200 OK):
```json
{
  "status": "SUCCESS",
  "data": [
    {
      "loadday": "2026-01-01",
      "meterload_h1": 0.009135780246912,
      "meterload_h2": 0.010357901975308,
      "...": "..."
    }
  ]
}
```

**Note**: Response does NOT include pod and dc fields — data is aggregated by loadday only.

---

## 3. POST /pod-forecast-batch-results

### Description
Retrieves forecast results for multiple PODs and returns them as a streaming response grouped by POD/DC. Optimized for large datasets to reduce memory footprint and improve time-to-first-byte.

### HTTP Method
POST

### Request Body
Type: BatchPodLoadRequest (same schema as API#2)

### Response
Type: StreamingResponse (application/json)

Streaming Structure:
```json
[
  {
    "pod": "POD123",
    "dc": "CNP",
    "forecast_results": [
      {
        "loadday": "2026-01-01",
        "meterload_h1": 0.004567890123456,
        "...": "..."
      }
    ]
  }
]
```

### Processing Flow
1. Converts BatchPodLoadRequest to internal format with result_format: "podloadhour"
2. Calls get_batch_results() to fetch forecast data for all PODs
3. Processes results via prepare_data_for_podloadhour_for_results()
4. Streams via stream_batch_results() async generator

### Use Case
Ideal for:
- Large batch exports (hundreds or thousands of PODs)
- Real-time dashboards that need progressive rendering
- API clients that can process streaming JSON
- Reducing server memory usage for large result sets

---

## Common Data Structures

### UEResponse
Generic response wrapper used by non-streaming endpoints.

```python
class UEResponse(BaseModel, Generic[T]):
    status: UEStatus  # "success", "failure", or "partial"
    message: Optional[str] = None
    data: T = None
```

### Load Type Column Prefixes
Results contain hourly load data with these column naming patterns:
- meterload_h1 to meterload_h25: Hourly meter load (hours 1-25)
- genload_h1 to genload_h25: Hourly generation load
- distributionload_h1 to distributionload_h25: Hourly distribution load
- ufeload_h1 to ufeload_h25: Hourly UFE (Unaccounted For Energy) load
- transmissionload_h1 to transmissionload_h25: Hourly transmission load

**Note**: Hour 25 represents the extra hour during daylight saving time transitions (fall back). Most days have hours 1-24.

### Date Format
- **Input**: MM/DD/YYYY (e.g., 07/15/2026)
- **Output**: YYYY-MM-DD (e.g., 2026-07-15)

---

## Error Scenarios

| Scenario | HTTP Status | Response |
|----------|-------------|----------|
| Missing one date parameter | 400 | "Both 'startdate' and 'enddate' must be provided together or omitted together." |
| enddate < startdate | 400 | "'enddate' must be greater than or equal to 'startdate'." |
| No results found | 400 | ForecastException: "No results found for the given input dataset" |
| Empty PODs list | 422 | Pydantic validation error (min_items=1) |
| Internal error | 500 | Exception details in response |

---

## API Comparison Matrix

| Feature | API#1 (GET) | API#2 (POST Aggregation) | API#3 (POST Streaming) |
|---------|-------------|-------------------------|----------------------|
| POD Count | Single | Multiple | Multiple |
| HTTP Method | GET | POST | POST |
| Response Type | JSON | JSON | Streaming JSON |
| Aggregation | No | Yes (by loadday) | No |
| POD Details in Response | Yes | No | Yes (nested) |
| Best For | Single POD lookup | Portfolio totals | Large batch exports |
| Memory Usage | Low | Medium | Low (streaming) |
| Time to First Byte | Medium | High | Low |
