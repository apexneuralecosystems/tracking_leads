# ApexNeural — Minimal Email Engagement Tracking

Track **opens** (pixel) and **clicks** (link) only. No IP, user-agent, location, or bot filtering.

- **Company:** ApexNeural  
- **Email tool:** Instantly.ai  
- **Tracking pixel:** `https://apexneural.com/o/{tracking_id}.png`  
- **Tracking link:** `https://apexneural.com/t/{tracking_id}`  

---

## Tech stack

FastAPI, PostgreSQL, async SQLAlchemy, Pydantic. All timestamps UTC.

---

## Database

- **leads:** id, tracking_id (unique), campaign_name (nullable), email, first_name, company, created_at (UTC), opened_at (UTC, nullable), first_click_at (UTC, nullable)  
- **events:** id, tracking_id, event_type (`open` | `click`), created_at (UTC)  

Migrations: Alembic. Run from project root:

```bash
# Set DATABASE_URL or ALEMBIC_DATABASE_URL (use postgresql+psycopg for Alembic)
alembic upgrade head
```

---

## API

| Method | Path | Behavior |
|--------|------|----------|
| GET | `/leads` | Get all leads. Optional: `?email=`, `?tracking_id=`, `?from_date=YYYY-MM-DD`, `?to_date=YYYY-MM-DD` (filter by created_at). |
| GET | `/leads/{id}` | Get one lead by UUID. |
| POST | `/leads` | Create lead: pass one of `lead_id` or `email`; optional: `campaign_name`. |
| DELETE | `/leads/{id}` | Delete lead by UUID. |
| GET | `/go/{campaign_name}/{tracking_id}` | **Only tracking endpoint.** Record click with campaign name, then redirect to `REDIRECT_BASE_URL` (e.g. …/go/DubaiCamp/t124). |
| POST | `/events` | Optional: log event (tracking_id, event_type open \| click). |

---

## Run

```bash
pip install -r requirements.txt
cp .env.example .env   # set DATABASE_URL
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

### Docker

Build and run (use env for `DATABASE_URL`; no secrets in image):

```bash
docker build -t apexneural-tracking .
docker run -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db -p 8000:8000 apexneural-tracking
```

Run migrations separately (same DB URL with `psycopg` for Alembic):

```bash
# Local or in a one-off container with DATABASE_URL set
alembic upgrade head
```

The `crm/` subfolder is excluded from the Docker build context (see `.dockerignore`).  

---

## Usage

- **Tracking link:** Use  
  `https://your-domain/go/{{campaign_name}}/{{tracking_id}}`  
  (e.g. `https://meetapexneural.com/go/DubaiCamp/t124`). Click is logged with campaign name, then the user is redirected to `REDIRECT_BASE_URL`.
# tracking_lads
