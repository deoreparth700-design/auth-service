import os
from datetime import datetime, timedelta, timezone

import jwt


def generate_access_token(user_id) -> str:
    payload = {
        "userId": user_id,
        # jsonwebtoken's expiresIn: "15m" -> encode iat/exp ourselves with PyJWT
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    return jwt.encode(payload, os.environ.get("JWT_ACCESS_SECRET"), algorithm="HS256")
