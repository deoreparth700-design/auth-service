import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from app.app import app
from app.db.pool import create_pool, close_pool


load_dotenv()


PORT = int(os.environ.get("PORT", 3000))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        pool = await create_pool()

        await pool.fetchval("SELECT NOW()")

        print("✅ Connected to PostgreSQL")

    except Exception as error:
        print("❌ Database connection failed")
        print(error)
        raise

    yield

    # Shutdown
    await close_pool()

    print("🔌 PostgreSQL connection pool closed")


app.router.lifespan_context = lifespan


def start_server():
    print(f"🚀 Server running on http://localhost:{PORT}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
    )


if __name__ == "__main__":
    start_server()