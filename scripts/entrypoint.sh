#!/usr/bin/env bash
# Run migrations then start the app. Use in Docker so the DB has tables on first deploy.
set -e
cd /app
if [ -n "${DATABASE_URL}" ]; then
  echo "Running database migrations..."
  alembic upgrade head
  echo "Migrations done."
else
  echo "WARNING: DATABASE_URL not set; skipping migrations."
fi
exec "$@"
