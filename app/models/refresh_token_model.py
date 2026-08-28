from datetime import datetime

from app.db.pool import get_pool


async def create_refresh_token(
    user_id: int,
    token_hash: str,
    expires_at: datetime,
):
    pool = get_pool()

    row = await pool.fetchrow(
        """
        INSERT INTO refresh_tokens (
            user_id,
            token_hash,
            expires_at
        )
        VALUES ($1, $2, $3)
        RETURNING id, user_id, expires_at, created_at
        """,
        user_id,
        token_hash,
        expires_at,
    )

    return dict(row) if row else None


async def find_refresh_token(token_hash: str):
    pool = get_pool()

    row = await pool.fetchrow(
        """
        SELECT *
        FROM refresh_tokens
        WHERE token_hash = $1
        """,
        token_hash,
    )

    return dict(row) if row else None


async def revoke_refresh_token(token_id: int):
    pool = get_pool()

    await pool.execute(
        """
        UPDATE refresh_tokens
        SET revoked_at = CURRENT_TIMESTAMP
        WHERE id = $1
          AND revoked_at IS NULL
        """,
        token_id,
    )