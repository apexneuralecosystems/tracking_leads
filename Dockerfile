# ApexNeural tracking microservice — production image.
# Build: docker build -t apexneural-tracking .
# Run: docker run -e DATABASE_URL=postgresql+asyncpg://... -p 8054:8054 apexneural-tracking

FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt


FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Non-root user for production
RUN addgroup --gid 1000 app && adduser --uid 1000 --gid 1000 --disabled-password --gecos "" app

COPY --from=builder /root/.local /home/app/.local
RUN chown -R app:app /home/app/.local
COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app
RUN chown -R app:app /app

USER app
ENV PATH="/home/app/.local/bin:$PATH"

# All config via env (no hardcoded secrets)
ENV HOST=0.0.0.0 \
    PORT=8054

EXPOSE 8054

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8054"]
