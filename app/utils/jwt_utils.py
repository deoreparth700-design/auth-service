import os
from datetime import datetime, timedelta, timezone

import jwt


def generate_access_token(user_id) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "userId": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=15),
    }

    return jwt.encode(
        payload,
        os.environ.get("JWT_ACCESS_SECRET"),
        algorithm="HS256",
    )


def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            os.environ.get("JWT_ACCESS_SECRET"),
            algorithms=["HS256"],
        )

        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None