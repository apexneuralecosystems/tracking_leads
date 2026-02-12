"""
Alembic env: use sync driver (psycopg) for migrations.
DATABASE_URL may be async (asyncpg); we convert to sync for Alembic.
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

# Load .env so get_settings sees it
load_dotenv()

# Use sync URL for Alembic (replace asyncpg with psycopg)
database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/tracking")
if "asyncpg" in database_url:
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
alembic_url = os.getenv("ALEMBIC_DATABASE_URL", database_url)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models so Base.metadata has tables
from app.database import Base  # noqa: E402
from app import models  # noqa: E402, F401

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = alembic_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = alembic_url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
