from datetime import datetime

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel

from app.models.user_model import (
    create_user,
    find_user_by_email,
    find_user_by_id,
)
from app.models.refresh_token_model import (
    create_refresh_token,
    find_refresh_token,
    revoke_refresh_token,
)
from app.utils.password_utils import (
    hash_password,
    compare_password,
)
from app.utils.jwt_utils import generate_access_token
from app.utils.auth_middleware import get_current_user
from app.utils.refresh_token_utils import (
    generate_refresh_token,
    hash_refresh_token,
    get_refresh_token_expiry,
)
from app.utils.rate_limiter import (
    is_rate_limited,
    record_failed_attempt,
    reset_attempts,
)


class SignupRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None


class LoginRequest(BaseModel):
    email: str | None = None
    password: str | None = None


class RefreshTokenRequest(BaseModel):
    refreshToken: str


class LogoutRequest(BaseModel):
    refreshToken: str


async def signup(body: SignupRequest):
    try:
        name, email, password = body.name, body.email, body.password

        if not name or not email or not password:
            raise HTTPException(
                status_code=400,
                detail="Name, email and password are required",
            )

        if "@" not in email:
            raise HTTPException(
                status_code=400,
                detail="Invalid email address",
            )

        if len(password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters",
            )

        existing_user = await find_user_by_email(email)

        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Email already registered",
            )

        password_hash = await hash_password(password)

        user = await create_user(
            name,
            email,
            password_hash,
        )

        return {
            "message": "User created successfully",
            "user": user,
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Signup error:", error)

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )


async def login(
    body: LoginRequest,
    request: Request,
):
    try:
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit before processing login
        if is_rate_limited(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Please try again later.",
            )

        email, password = body.email, body.password

        if not email or not password:
            record_failed_attempt(client_ip)

            raise HTTPException(
                status_code=400,
                detail="Email and password are required",
            )

        user = await find_user_by_email(email)

        if not user:
            record_failed_attempt(client_ip)

            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        password_matches = await compare_password(
            password,
            user["password_hash"],
        )

        if not password_matches:
            record_failed_attempt(client_ip)

            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        # Successful login clears failed attempts
        reset_attempts(client_ip)

        # Generate short-lived access token
        access_token = generate_access_token(user["id"])

        # Generate long-lived refresh token
        refresh_token = generate_refresh_token()

        # Hash refresh token before storing it
        refresh_token_hash = hash_refresh_token(
            refresh_token
        )

        # Set refresh token expiration
        refresh_token_expiry = get_refresh_token_expiry()

        # Store hashed refresh token in database
        await create_refresh_token(
            user["id"],
            refresh_token_hash,
            refresh_token_expiry,
        )

        return {
            "message": "Login successful",
            "accessToken": access_token,
            "refreshToken": refresh_token,
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Login error:", error)

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )


async def get_me(
    user=Depends(get_current_user),
):
    return {
        "user": user,
    }


async def refresh_access_token(
    body: RefreshTokenRequest,
):
    try:
        refresh_token = body.refreshToken

        token_hash = hash_refresh_token(refresh_token)

        stored_token = await find_refresh_token(token_hash)

        if not stored_token:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
            )

        if stored_token["revoked_at"] is not None:
            raise HTTPException(
                status_code=401,
                detail="Refresh token has been revoked",
            )

        if stored_token["expires_at"] <= datetime.now():
            raise HTTPException(
                status_code=401,
                detail="Refresh token has expired",
            )

        user = await find_user_by_id(
            stored_token["user_id"]
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found",
            )

        # Revoke old refresh token
        await revoke_refresh_token(
            stored_token["id"]
        )

        # Generate new refresh token
        new_refresh_token = generate_refresh_token()

        new_refresh_token_hash = hash_refresh_token(
            new_refresh_token
        )

        new_refresh_token_expiry = get_refresh_token_expiry()

        # Store new refresh token
        await create_refresh_token(
            user["id"],
            new_refresh_token_hash,
            new_refresh_token_expiry,
        )

        # Generate new access token
        new_access_token = generate_access_token(
            user["id"]
        )

        return {
            "message": "Token refreshed successfully",
            "accessToken": new_access_token,
            "refreshToken": new_refresh_token,
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Refresh token error:", error)

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )


async def logout(
    body: LogoutRequest,
):
    try:
        refresh_token = body.refreshToken

        token_hash = hash_refresh_token(refresh_token)

        stored_token = await find_refresh_token(token_hash)

        if not stored_token:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
            )

        if stored_token["revoked_at"] is not None:
            raise HTTPException(
                status_code=401,
                detail="Refresh token has already been revoked",
            )

        await revoke_refresh_token(
            stored_token["id"]
        )

        return {
            "message": "Logout successful",
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Logout error:", error)

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )