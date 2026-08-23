import asyncio
import os

from app.db.pool import create_pool, close_pool


async def migrate() -> None:
    try:
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = f.read()

        pool = await create_pool()
        await pool.execute(schema)

        print("✅ Database migration completed")
    except Exception as error:
        print("❌ Migration failed")
        print(error)
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(migrate())
