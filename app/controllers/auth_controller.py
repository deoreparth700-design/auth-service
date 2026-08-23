from fastapi import HTTPException
from pydantic import BaseModel

from app.models.user_model import create_user, find_user_by_email
from app.utils.password_utils import hash_password, compare_password
from app.utils.jwt_utils import generate_access_token


class SignupRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None


class LoginRequest(BaseModel):
    email: str | None = None
    password: str | None = None


async def signup(body: SignupRequest):
    try:
        name, email, password = body.name, body.email, body.password

        if not name or not email or not password:
            raise HTTPException(
                status_code=400,
                detail="Name, email and password are required",
            )

        if "@" not in email:
            raise HTTPException(status_code=400, detail="Invalid email address")

        if len(password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters",
            )

        existing_user = await find_user_by_email(email)

        if existing_user:
            raise HTTPException(status_code=409, detail="Email already registered")

        password_hash = await hash_password(password)

        user = await create_user(name, email, password_hash)

        return {
            "message": "User created successfully",
            "user": user,
        }

    except HTTPException:
        raise
    except Exception as error:
        print("Signup error:", error)
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def login(body: LoginRequest):
    try:
        email, password = body.email, body.password

        if not email or not password:
            raise HTTPException(
                status_code=400,
                detail="Email and password are required",
            )

        user = await find_user_by_email(email)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        password_matches = await compare_password(password, user["password_hash"])

        if not password_matches:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token = generate_access_token(user["id"])

        return {
            "message": "Login successful",
            "accessToken": access_token,
        }

    except HTTPException:
        raise
    except Exception as error:
        print("Login error:", error)
        raise HTTPException(status_code=500, detail="Internal Server Error")
