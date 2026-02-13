# ApexNeural Lead Tracking — Frontend

Standalone React frontend for the tracking leads API. Uses ApexNeural Design System (colors, typography, spacing, components).

**Location:** Separate from the `crm` backend repo — this folder lives at `apexneural/frontend`.

## Setup

```bash
cd frontend
npm install
```

## Configure API URL

Create `.env` (or use `.env.example`):

```
VITE_API_BASE_URL=https://api.meetapexneural.com
```

## Run

```bash
npm run dev
```

Open http://localhost:3000

## Build

```bash
npm run build
```

Output in `dist/`. Serve with any static host.

## Features

- **Leads list** — table with filters: email, tracking_id, from_date, to_date
- **Create lead** — form with lead_id OR email, optional campaign_name
- **Lead detail** — view one lead, delete

All requests go to `VITE_API_BASE_URL` (e.g. https://api.meetapexneural.com).
