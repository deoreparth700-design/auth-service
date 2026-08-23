import asyncio
import os

import uvicorn
from dotenv import load_dotenv

from app.app import app
from app.db.pool import create_pool

load_dotenv()

PORT = int(os.environ.get("PORT", 3000))


@app.on_event("startup")
async def startup_event():
    try:
        pool = await create_pool()
        await pool.fetchval("SELECT NOW()")
        print("✅ Connected to PostgreSQL")
    except Exception as error:
        print("❌ Database connection failed")
        print(error)


def start_server():
    print(f"🚀 Server running on http://localhost:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    start_server()
