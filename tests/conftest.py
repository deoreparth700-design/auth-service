import os
import ssl
import urllib.parse
import pytest
from dotenv import load_dotenv
import asyncpg
from httpx import AsyncClient, ASGITransport

# Load any .env variables before checking environment
load_dotenv()

# 1. Read TEST_DATABASE_URL and validate
test_db_url = os.environ.get("TEST_DATABASE_URL")
if not test_db_url:
    pytest.exit("TEST_DATABASE_URL environment variable is missing", returncode=1)

db_url = os.environ.get("DATABASE_URL")
if db_url and test_db_url.strip() == db_url.strip():
    pytest.exit("TEST_DATABASE_URL cannot equal DATABASE_URL", returncode=1)

parsed = urllib.parse.urlparse(test_db_url)
db_name = parsed.path.lstrip("/").split("?")[0]
if "test" not in db_name.lower():
    pytest.exit(f"TEST_DATABASE_URL database name '{db_name}' must contain 'test'", returncode=1)

# 2. Set DATABASE_URL and JWT_ACCESS_SECRET BEFORE importing the app
os.environ["DATABASE_URL"] = test_db_url
os.environ["JWT_ACCESS_SECRET"] = "test-jwt-access-secret-for-testing-only"

from app.app import app
import app.db.pool as db_pool
from app.utils.rate_limiter import _login_attempts


@pytest.fixture(scope="session", autouse=True)
async def setup_database_pool():
    pool = None
    try:
        pool = await asyncpg.create_pool(dsn=test_db_url, ssl=False)
    except Exception:
        pool = await asyncpg.create_pool(
            dsn=test_db_url, ssl=ssl.create_default_context()
        )

    db_pool._pool = pool

    # Create tables from app/db/schema.sql
    schema_path = os.path.join(
        os.path.dirname(__file__), "..", "app", "db", "schema.sql"
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    await pool.execute(schema_sql)

    yield pool

    await pool.close()
    db_pool._pool = None


@pytest.fixture(autouse=True)
async def clean_database_and_state(setup_database_pool):
    pool = setup_database_pool
    await pool.execute("TRUNCATE users, refresh_tokens RESTART IDENTITY CASCADE;")
    _login_attempts.clear()
    yield
    await pool.execute("TRUNCATE users, refresh_tokens RESTART IDENTITY CASCADE;")
    _login_attempts.clear()


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
