# Tracking API — Frontend integration

Base URL (replace with your deployed URL):

```
https://your-api-domain.com
```

Local: `http://localhost:8000`

- All request/response bodies are **JSON**.
- All datetime fields are **ISO 8601** (e.g. `2026-02-12T14:30:00Z`).
- **CORS** is enabled for all origins.

---

## 1. Health

**GET** `/health`

No query or body.

**Response:** `200`

```json
{ "status": "ok" }
```

**Example (fetch):**

```javascript
const res = await fetch(`${BASE_URL}/health`);
const data = await res.json(); // { status: "ok" }
```

---

## 2. List leads (with filters)

**GET** `/leads`

**Query (all optional):**

| Param         | Type   | Description                                      |
|---------------|--------|--------------------------------------------------|
| `email`       | string | Filter by email                                  |
| `tracking_id` | string | Filter by tracking_id (lead_id)                  |
| `from_date`   | string | YYYY-MM-DD — leads created on or after this date |
| `to_date`     | string | YYYY-MM-DD — leads created on or before this date |

Rules: if both `from_date` and `to_date` are sent, `from_date` must be ≤ `to_date` (else 400).

**Response:** `200` — array of lead objects.

```json
[
  {
    "id": "uuid",
    "tracking_id": "string",
    "campaign_name": "string | null",
    "email": "string",
    "first_name": "string | null",
    "company": "string | null",
    "created_at": "2026-02-12T10:00:00Z",
    "opened_at": null,
    "first_click_at": "2026-02-12T14:30:00Z"
  }
]
```

**Example (fetch):**

```javascript
const params = new URLSearchParams();
if (email) params.set('email', email);
if (trackingId) params.set('tracking_id', trackingId);
if (fromDate) params.set('from_date', fromDate);   // "2026-02-01"
if (toDate) params.set('to_date', toDate);         // "2026-02-28"

const res = await fetch(`${BASE_URL}/leads?${params}`);
const leads = await res.json();
```

---

## 3. Get one lead by ID

**GET** `/leads/{id}`

`{id}` = lead UUID.

**Response:** `200` — single lead object (same shape as in list).  
**Error:** `404` if not found.

**Example (fetch):**

```javascript
const res = await fetch(`${BASE_URL}/leads/${leadId}`);
if (!res.ok) throw new Error(await res.text());
const lead = await res.json();
```

---

## 4. Create lead

**POST** `/leads`  
**Content-Type:** `application/json`

**Body:** Pass **exactly one** of `lead_id` or `email`. Optionally `campaign_name`.

```json
{
  "lead_id": "t124",
  "campaign_name": "DubaiCamp"
}
```

or

```json
{
  "email": "lead@example.com",
  "campaign_name": "DubaiCamp"
}
```

| Field          | Type   | Required | Description                    |
|----------------|--------|----------|--------------------------------|
| `lead_id`      | string | one of   | Tracking ID (use this OR email) |
| `email`        | string | one of   | Email (use this OR lead_id)    |
| `campaign_name`| string | no       | Campaign name                  |

**Response:** `201` — created lead (same shape as in list).  
**Error:** `409` if `lead_id` or `email` already exists; `422` if validation fails (e.g. both or neither of lead_id/email).

**Example (fetch):**

```javascript
const res = await fetch(`${BASE_URL}/leads`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ lead_id: 't124', campaign_name: 'DubaiCamp' }),
});
const lead = await res.json();
```

---

## 5. Delete lead

**DELETE** `/leads/{id}`

`{id}` = lead UUID.

**Response:** `204` No Content (empty body).  
**Error:** `404` if not found.

**Example (fetch):**

```javascript
const res = await fetch(`${BASE_URL}/leads/${leadId}`, { method: 'DELETE' });
if (res.status === 204) { /* deleted */ }
```

---

## 6. Tracking link (redirect)

**GET** `/go/{campaign_name}/{tracking_id}`

Not called from your frontend JS — use as **href** in emails or landing pages. When the user clicks, the API records the click and redirects to your `REDIRECT_BASE_URL`.

**Example link:**

```
https://your-api-domain.com/go/DubaiCamp/t124
```

---

## 7. Log event (optional)

**POST** `/events`  
**Content-Type:** `application/json`

**Body:**

```json
{
  "tracking_id": "t124",
  "event_type": "click"
}
```

`event_type`: `"open"` or `"click"`.

**Response:** `201` — event object with `id`, `tracking_id`, `event_type`, `created_at`.

**Example (fetch):**

```javascript
const res = await fetch(`${BASE_URL}/events`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ tracking_id: 't124', event_type: 'click' }),
});
const event = await res.json();
```

---

## Summary table

| Method | Path                          | Use from frontend                    |
|--------|-------------------------------|--------------------------------------|
| GET    | `/health`                     | Health check                         |
| GET    | `/leads`                     | List leads (filters: email, tracking_id, from_date, to_date) |
| GET    | `/leads/{id}`                | Get one lead                         |
| POST   | `/leads`                     | Create lead (lead_id or email)       |
| DELETE | `/leads/{id}`                | Delete lead                          |
| GET    | `/go/{campaign_name}/{tracking_id}` | Use as link URL (no JS call)  |
| POST   | `/events`                    | Optional: log open/click event       |

---

## TypeScript types (optional)

```ts
interface Lead {
  id: string;
  tracking_id: string;
  campaign_name: string | null;
  email: string;
  first_name: string | null;
  company: string | null;
  created_at: string;
  opened_at: string | null;
  first_click_at: string | null;
}

interface CreateLeadBody {
  lead_id?: string;
  email?: string;
  campaign_name?: string;
}
```

---

## Swagger / ReDoc

- **Swagger UI:** `GET /docs`
- **ReDoc:** `GET /redoc`

Use these in the browser for interactive testing and full schema details.
