# Frontend connectivity to CRM API

This doc summarizes how the frontend connects to the backend and what changed so the UI stays in sync.

---

## Base URL and config

| Item | Value |
|------|--------|
| **API base URL** | `https://api.meetapexneural.com` |
| **Frontend env (example)** | `VITE_API_BASE_URL` (no trailing slash) |
| **Auth** | None. All endpoints are unauthenticated. |
| **CORS** | Allowed from any origin (`*`) when `CORS_ORIGINS=*`. For production you can restrict to your frontend origin. |

Use the base URL for all requests, e.g. `fetch(\`${baseUrl}/leads\`)`.

---

## Changes that affect the frontend

These are the updates made on the backend; the frontend should rely on the current behaviour below.

| Change | Impact on frontend |
|--------|--------------------|
| **Lead response: no `first_name` or `company`** | Do not read or display these fields; they are no longer in the API response. |
| **`opened_at`** | “When they first opened” (e.g. email). Set when **POST /events** is called with `event_type: "open"` for that lead’s `tracking_id`. Can be `null` until an open event is sent. |
| **`first_click_at`** | “When they clicked the tracking link.” Set when the user hits **GET /go/{campaign_name}/{tracking_id}**. Can be `null` if they never clicked. |
| **Tracking link path** | Use the lead’s **`tracking_id`** (e.g. `"001"`, `"run-py-001"`) in the URL, **not** the lead’s UUID `id`. Example: `https://api.meetapexneural.com/go/dubai/001`. |
| **Swagger “Execute” for /go** | May show “Failed to fetch” (browser/CORS on redirect). Test tracking links in the address bar or via a normal link, not from Swagger. |

---

## Current lead response shape

Every lead in **GET /leads** and **GET /leads/{id}**, and the body of **POST /leads**, looks like this (no `first_name`, no `company`):

```json
{
  "id": "6a63c6ec-d64d-49af-b7d9-90f56d6f9e32",
  "tracking_id": "001",
  "campaign_name": "dubai",
  "email": "",
  "created_at": "2026-02-13T07:34:49.054177Z",
  "opened_at": null,
  "first_click_at": "2026-02-13T07:35:12.742161Z"
}
```

| Field | Type | Meaning |
|-------|------|--------|
| `id` | UUID string | Lead primary key; use for GET by id and DELETE. |
| `tracking_id` | string | Short id for this lead; use in tracking URLs and filters. |
| `campaign_name` | string \| null | Campaign name. |
| `email` | string | Email (can be `""` if lead was created with only `lead_id`). |
| `created_at` | string (ISO 8601) | When the lead was created. |
| `opened_at` | string \| null | When they first opened (e.g. email); set by POST /events with `event_type: "open"`. |
| `first_click_at` | string \| null | When they first clicked the tracking link. |

---

## Endpoints quick reference

| Method | Path | Request body | Response |
|--------|------|--------------|----------|
| GET | `/health` | — | `{ "status": "ok" }` |
| GET | `/leads` | — (optional query: `email`, `tracking_id`, `from_date`, `to_date`) | Array of leads (shape above) |
| GET | `/leads/{lead_id}` | — (`lead_id` = UUID) | Single lead (shape above) |
| POST | `/leads` | `{ lead_id? or email?, campaign_name? }` | Created lead (shape above) |
| DELETE | `/leads/{lead_id}` | — | 204 No Content |
| POST | `/events` | `{ tracking_id, event_type: "open" \| "click" }` | Created event |
| GET | `/go/{campaign_name}/{tracking_id}` | — | 302 redirect (use lead’s `tracking_id`, not `id`) |

---

## TypeScript / JSDoc types (current)

See `src/api/types.js` for JSDoc typedefs. Equivalent TypeScript:

```ts
interface Lead {
  id: string;
  tracking_id: string;
  campaign_name: string | null;
  email: string;
  created_at: string;
  opened_at: string | null;   // when they first opened (e.g. email)
  first_click_at: string | null;   // when they clicked the tracking link
}

interface LeadCreate {
  lead_id?: string;
  email?: string;
  campaign_name?: string | null;
}

interface EventCreate {
  tracking_id: string;
  event_type: "open" | "click";
}

interface Event {
  id: string;
  tracking_id: string;
  event_type: "open" | "click";
  created_at: string;
}

interface ApiError {
  detail: string | Array<{ loc: string[]; msg: string; type?: string }>;
}
```

---

## Frontend usage

- **Config:** `src/config.js` — `API_BASE_URL` from `VITE_API_BASE_URL` or default; in dev, `/api` is proxied to the API (see `vite.config.js`).
- **Client:** `src/api/client.js` — `api.getLeads`, `api.getLead`, `api.createLead`, `api.deleteLead`, `api.createEvent`; `getTrackingUrl(campaignName, trackingId)` uses **tracking_id**, not lead id.
- **UI:** Leads list and lead detail show only **tracking_id**, **campaign_name**, **opened_at**, and Delete.

For full request/response examples and error codes, see the backend **API_REFERENCE_FRONTEND.md** (or equivalent in the API repo).
