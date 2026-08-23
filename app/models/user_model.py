from app.db.pool import get_pool


async def create_user(name: str, email: str, password_hash: str):
    pool = get_pool()
    row = await pool.fetchrow(
        """INSERT INTO users (name, email, password_hash)
           VALUES ($1, $2, $3)
           RETURNING id, name, email, created_at""",
        name, email, password_hash,
    )
    return dict(row) if row else None


async def find_user_by_email(email: str):
    pool = get_pool()
    row = await pool.fetchrow(
        """SELECT *
           FROM users
           WHERE email = $1""",
        email,
    )
    return dict(row) if row else None


async def find_user_by_id(user_id: int):
    pool = get_pool()
    row = await pool.fetchrow(
        """SELECT id, name, email, created_at
           FROM users
           WHERE id = $1""",
        user_id,
    )
    return dict(row) if row else None
