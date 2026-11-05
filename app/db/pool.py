import os
import ssl

import asyncpg
from dotenv import load_dotenv


load_dotenv()


_pool: asyncpg.Pool | None = None


async def create_pool() -> asyncpg.Pool:
    """Create and return the shared PostgreSQL connection pool."""

    global _pool

    if _pool is not None:
        return _pool

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set"
        )

    # Use SSL unless the connection string explicitly disables it.
    # Production databases (e.g. Neon / Render) require SSL;
    # local and Docker Compose Postgres do not support it.
    ssl_option: ssl.SSLContext | bool
    if "sslmode=disable" in database_url:
        ssl_option = False
    else:
        ssl_option = ssl.create_default_context()

    _pool = await asyncpg.create_pool(
        dsn=database_url,
        ssl=ssl_option,
    )

    return _pool


def get_pool() -> asyncpg.Pool:
    """Return the initialized PostgreSQL connection pool."""

    if _pool is None:
        raise RuntimeError(
            "Database pool has not been initialized"
        )

    return _pool


async def close_pool() -> None:
    """Close the PostgreSQL connection pool."""

    global _pool

    if _pool is not None:
        await _pool.close()
        _pool = None
