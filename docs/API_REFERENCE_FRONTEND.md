# API Reference for Frontend

**Base URL:** `https://api.meetapexneural.com` (or from env, e.g. `VITE_API_BASE_URL`)

All timestamps are ISO 8601 with Z (UTC). UUIDs are standard UUID v4 strings.

---

## 1. Health

### GET /health

**Request:** No body. No query params.

**Response:** `200 OK`

```json
{
  "status": "ok"
}
```

---

## 2. Leads

### GET /leads

**Request:** No body. Optional query params:

| Param        | Type   | Required | Description                                              |
|-------------|--------|----------|----------------------------------------------------------|
| email       | string | No       | Filter by exact email                                    |
| tracking_id | string | No       | Filter by tracking_id (the short id, not UUID)           |
| from_date   | string | No       | YYYY-MM-DD, leads created on or after this date          |
| to_date     | string | No       | YYYY-MM-DD, leads created on or before this date         |

**Example:** `GET /leads?email=alice@example.com&from_date=2025-01-01&to_date=2025-12-31`

**Response:** `200 OK`

```json
[
  {
    "id": "a664a549-3a95-4e42-9f29-3c2a7b1f0e1a",
    "tracking_id": "run-py-001",
    "campaign_name": "DubaiCamp",
    "email": "",
    "created_at": "2026-02-13T07:42:14.347270Z",
    "opened_at": null,
    "first_click_at": null
  }
]
```

`first_click_at` = when they clicked the tracking link (null if not yet clicked). `opened_at` = when they first opened (e.g. email); set when POST /events is called with `event_type: "open"` for that lead’s tracking_id (null until then).

**Error:** `400` if `from_date` > `to_date` (e.g. `{"detail": "from_date must be on or before to_date"}`).

---

### GET /leads/{lead_id}

**Request:** No body. Path param `lead_id` = lead UUID (e.g. `a664a549-3a95-4e42-9f29-3c2a7b1f0e1a`).

**Response:** `200 OK`

```json
{
  "id": "a664a549-3a95-4e42-9f29-3c2a7b1f0e1a",
  "tracking_id": "run-py-001",
  "campaign_name": "DubaiCamp",
  "email": "",
  "created_at": "2026-02-13T07:42:14.347270Z",
  "opened_at": null,
  "first_click_at": null
}
```

**Error:** `404` — `{"detail": "Lead not found"}`

---

### POST /leads

**Request body:** JSON. Provide **exactly one** of `lead_id` or `email` (not both).

| Field         | Type   | Required | Description |
|---------------|--------|----------|-------------|
| lead_id       | string | One of two | Tracking ID (1–128 chars). Use this OR email. |
| email         | string | One of two | Email (1–320 chars). Use this OR lead_id. |
| campaign_name | string | No       | Optional campaign name (max 256). |

**Example (by tracking id):**

```json
{
  "lead_id": "run-py-001",
  "campaign_name": "DubaiCamp"
}
```

**Example (by email):**

```json
{
  "email": "alice@example.com",
  "campaign_name": "Webinar2025"
}
```

**Response:** `201 Created`

```json
{
  "id": "a664a549-3a95-4e42-9f29-3c2a7b1f0e1a",
  "tracking_id": "run-py-001",
  "campaign_name": "DubaiCamp",
  "email": "",
  "created_at": "2026-02-13T07:42:14.347270Z",
  "opened_at": null,
  "first_click_at": null
}
```

**Errors:**

- `409` — `{"detail": "Lead with this tracking_id already exists"}` or `{"detail": "Lead with this email already exists"}`
- `422` — Validation error if both/neither of `lead_id` or `email` provided (e.g. `{"detail": [{"loc": ["body", "..."], "msg": "..."}]}`)

---

### DELETE /leads/{lead_id}

**Request:** No body. Path param `lead_id` = lead UUID.

**Response:** `204 No Content` (empty body).

**Error:** `404` — `{"detail": "Lead not found"}`

---

## 3. Events

### POST /events

**Request body:** JSON

| Field        | Type   | Required | Description |
|--------------|--------|----------|-------------|
| tracking_id  | string | Yes      | 1–128 chars (must match a lead’s tracking_id if you want lead stats updated via /go). |
| event_type   | string | Yes      | Literal `"open"` or `"click"`. |

**Example:**

```json
{
  "tracking_id": "run-py-001",
  "event_type": "open"
}
```

**Response:** `201 Created`

```json
{
  "id": "a62ff8fb-12b8-47f2-8173-3946ea6f8920",
  "tracking_id": "run-py-001",
  "event_type": "open",
  "created_at": "2026-02-13T07:42:16.454334Z"
}
```

**Error:** `422` if `event_type` is not `open` or `click`, or validation fails.

---

## 4. Tracking (redirect link)

### GET /go/{campaign_name}/{tracking_id}

**Request:** No body. Path params:

- `campaign_name` — string (e.g. `dubai`, `DubaiCamp`).
- `tracking_id` — **lead’s tracking_id** (e.g. `001`, `run-py-001`), **not** the lead’s UUID.

**Example URL:** `https://api.meetapexneural.com/go/dubai/001`

**Response:** `302 Found` with header `Location: <REDIRECT_BASE_URL>`. No JSON body; browser or client should follow redirect.

**Note:** Testing from Swagger may show “Failed to fetch” (browser/CORS on redirect). Test in browser address bar or with `curl -I "https://api.meetapexneural.com/go/dubai/001"`.

---

## Summary table

| Method | Path                     | Request body      | Response body          | Status   |
|--------|--------------------------|-------------------|-------------------------|----------|
| GET    | /health                  | —                 | `{ "status": "ok" }`    | 200      |
| GET    | /leads                   | — (query params)  | `LeadResponse[]`        | 200      |
| GET    | /leads/{lead_id}         | —                 | `LeadResponse`         | 200      |
| POST   | /leads                   | `LeadCreate`      | `LeadResponse`         | 201      |
| DELETE | /leads/{lead_id}         | —                 | (empty)                 | 204      |
| POST   | /events                  | `EventCreate`     | `EventResponse`        | 201      |
| GET    | /go/{campaign_name}/{tracking_id} | —         | (redirect, no body)     | 302      |

---

## TypeScript / frontend types (optional)

```ts
// Lead (response) — no first_name/company; first_click_at = when they clicked the link
interface Lead {
  id: string;
  tracking_id: string;
  campaign_name: string | null;
  email: string;
  created_at: string;   // ISO 8601
  opened_at: string | null;   // when they first opened (e.g. email)
  first_click_at: string | null;   // when they clicked the tracking link
}

// Create lead: pass either lead_id or email, not both
interface LeadCreate {
  lead_id?: string;
  email?: string;
  campaign_name?: string | null;
}

// Event (response)
interface Event {
  id: string;
  tracking_id: string;
  event_type: "open" | "click";
  created_at: string;
}

// Create event
interface EventCreate {
  tracking_id: string;
  event_type: "open" | "click";
}

// Error payload (4xx/5xx)
interface ApiError {
  detail: string | Array<{ loc: string[]; msg: string; type?: string }>;
}
```
