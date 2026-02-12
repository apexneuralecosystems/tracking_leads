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

- **leads:** id, tracking_id (unique), email, first_name, company, created_at (UTC), opened_at (UTC, nullable), first_click_at (UTC, nullable)  
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
| GET | `/leads` | List all leads with engagement (id, tracking_id, email, opened_at, first_click_at). |
| POST | `/leads` | Create lead (tracking_id, email, first_name, company). |
| GET | `/o/{tracking_id}.png` | Store first **open** per tracking_id (no duplicate opens), return 1×1 transparent PNG. No redirect. |
| GET | `/t/{tracking_id}` | Store **click**, then redirect to `REDIRECT_BASE_URL` (default https://apexneural.com). Event stored before redirect. |
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
- Health: http://localhost:8000/healthz  

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

## Instantly usage

- **Open tracking:** In your email HTML, add  
  `<img src="https://apexneural.com/o/{{tracking_id}}.png" width="1" height="1" alt="" />`  
  (Use your merge field for `tracking_id`.)

- **Click tracking:** Use link  
  `https://apexneural.com/t/{{tracking_id}}`  
  so each recipient has a unique link; click is logged then they are redirected to your site.
# tracking_lads
