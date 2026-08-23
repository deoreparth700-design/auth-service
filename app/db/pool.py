import os
import ssl

import asyncpg
from dotenv import load_dotenv

load_dotenv()

_pool: asyncpg.Pool | None = None


async def create_pool() -> asyncpg.Pool:
    """Create (once) and return the shared connection pool.

    Mirrors src/db/pool.js, which builds a `pg.Pool` with
    `ssl: { rejectUnauthorized: false }`.
    """
    global _pool

    if _pool is None:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        _pool = await asyncpg.create_pool(
            dsn=os.environ.get("DATABASE_URL"),
            ssl=ssl_context,
        )

    return _pool


def get_pool() -> asyncpg.Pool:
    """Return the already-created pool. Raises if called before create_pool()."""
    if _pool is None:
        raise RuntimeError("Pool has not been created yet. Call create_pool() first.")
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
