import pytest
from httpx import AsyncClient


# 1. Signup success
async def test_signup_success(client: AsyncClient):
    res = await client.post(
        "/api/auth/signup",
        json={
            "name": "Alice Developer",
            "email": "alice@example.com",
            "password": "securepassword123",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["message"] == "User created successfully"
    assert "user" in data
    assert data["user"]["name"] == "Alice Developer"
    assert data["user"]["email"] == "alice@example.com"
    assert "id" in data["user"]
    assert "password_hash" not in data["user"]


# 2. Duplicate email -> 409
async def test_signup_duplicate_email(client: AsyncClient):
    await client.post(
        "/api/auth/signup",
        json={
            "name": "Alice Developer",
            "email": "alice@example.com",
            "password": "securepassword123",
        },
    )
    res = await client.post(
        "/api/auth/signup",
        json={
            "name": "Alice Clone",
            "email": "alice@example.com",
            "password": "anotherpassword123",
        },
    )
    assert res.status_code == 409
    assert res.json()["detail"] == "Email already registered"


# 3. Missing fields -> 400
@pytest.mark.parametrize(
    "payload",
    [
        {"email": "alice@example.com", "password": "securepassword123"},
        {"name": "Alice Developer", "password": "securepassword123"},
        {"name": "Alice Developer", "email": "alice@example.com"},
        {},
    ],
)
async def test_signup_missing_fields(client: AsyncClient, payload: dict):
    res = await client.post("/api/auth/signup", json=payload)
    assert res.status_code == 400
    assert res.json()["detail"] == "Name, email and password are required"


# 4. Bad email -> 400
async def test_signup_bad_email(client: AsyncClient):
    res = await client.post(
        "/api/auth/signup",
        json={
            "name": "Bad Email User",
            "email": "invalidemailformat",
            "password": "securepassword123",
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Invalid email address"


async def test_signup_email_without_valid_domain(client: AsyncClient):
    res = await client.post(
        "/api/auth/signup",
        json={
            "name": "Invalid Domain User",
            "email": "a@b",
            "password": "securepassword123",
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Invalid email address"


# 5. Password under 8 chars -> 400
async def test_signup_password_under_8_chars(client: AsyncClient):
    res = await client.post(
        "/api/auth/signup",
        json={
            "name": "Short Password User",
            "email": "short@example.com",
            "password": "pass7",
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Password must be at least 8 characters"


async def test_signup_password_longer_than_72_bytes(client: AsyncClient):
    res = await client.post(
        "/api/auth/signup",
        json={
            "name": "Long Password User",
            "email": "longpass@example.com",
            "password": "a" * 73,
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Password must be at most 72 bytes"


async def test_signup_password_exactly_72_bytes_works(client: AsyncClient):
    res = await client.post(
        "/api/auth/signup",
        json={
            "name": "Max Password User",
            "email": "maxpass@example.com",
            "password": "a" * 72,
        },
    )
    assert res.status_code == 200
    assert res.json()["message"] == "User created successfully"


# 6. Login success returns accessToken and refreshToken
async def test_login_success(client: AsyncClient):
    await client.post(
        "/api/auth/signup",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "securepassword123",
        },
    )
    res = await client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "securepassword123",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["message"] == "Login successful"
    assert "accessToken" in data
    assert "refreshToken" in data
    assert isinstance(data["accessToken"], str) and len(data["accessToken"]) > 0
    assert isinstance(data["refreshToken"], str) and len(data["refreshToken"]) > 0


# 7. Wrong password -> 401
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/auth/signup",
        json={
            "name": "Wrong Pass User",
            "email": "wrongpass@example.com",
            "password": "securepassword123",
        },
    )
    res = await client.post(
        "/api/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "wrongpassword999",
        },
    )
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid email or password"


# 8. Unknown email -> 401
async def test_login_unknown_email(client: AsyncClient):
    res = await client.post(
        "/api/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "securepassword123",
        },
    )
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid email or password"


# 9. /me with a valid token works
async def test_me_with_valid_token(client: AsyncClient):
    await client.post(
        "/api/auth/signup",
        json={
            "name": "Me User",
            "email": "me@example.com",
            "password": "securepassword123",
        },
    )
    login_res = await client.post(
        "/api/auth/login",
        json={
            "email": "me@example.com",
            "password": "securepassword123",
        },
    )
    access_token = login_res.json()["accessToken"]

    res = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "user" in data
    assert data["user"]["email"] == "me@example.com"
    assert data["user"]["name"] == "Me User"


# 10. /me with no or invalid token -> 401
async def test_me_with_invalid_token(client: AsyncClient):
    res = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid or expired token"


async def test_me_with_no_token(client: AsyncClient):
    res = await client.get("/api/auth/me")
    assert res.status_code == 401
    assert res.headers.get("www-authenticate") == "Bearer"


# 11. Refresh returns new tokens and the OLD refresh token then fails
async def test_refresh_token_rotation_and_invalidation(client: AsyncClient):
    await client.post(
        "/api/auth/signup",
        json={
            "name": "Refresh User",
            "email": "refresh@example.com",
            "password": "securepassword123",
        },
    )
    login_res = await client.post(
        "/api/auth/login",
        json={
            "email": "refresh@example.com",
            "password": "securepassword123",
        },
    )
    old_refresh_token = login_res.json()["refreshToken"]

    # First refresh succeeds
    refresh_res = await client.post(
        "/api/auth/refresh",
        json={"refreshToken": old_refresh_token},
    )
    assert refresh_res.status_code == 200
    refresh_data = refresh_res.json()
    assert "accessToken" in refresh_data
    assert "refreshToken" in refresh_data
    new_refresh_token = refresh_data["refreshToken"]
    assert new_refresh_token != old_refresh_token

    # Using the old refresh token a second time must fail
    old_token_res = await client.post(
        "/api/auth/refresh",
        json={"refreshToken": old_refresh_token},
    )
    assert old_token_res.status_code == 401
    assert old_token_res.json()["detail"] == "Refresh token has been revoked"

    # Using the new refresh token succeeds
    new_refresh_res = await client.post(
        "/api/auth/refresh",
        json={"refreshToken": new_refresh_token},
    )
    assert new_refresh_res.status_code == 200


# 12. Logout revokes the refresh token
async def test_logout_revokes_token(client: AsyncClient):
    await client.post(
        "/api/auth/signup",
        json={
            "name": "Logout User",
            "email": "logout@example.com",
            "password": "securepassword123",
        },
    )
    login_res = await client.post(
        "/api/auth/login",
        json={
            "email": "logout@example.com",
            "password": "securepassword123",
        },
    )
    refresh_token = login_res.json()["refreshToken"]

    logout_res = await client.post(
        "/api/auth/logout",
        json={"refreshToken": refresh_token},
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Logout successful"

    # Refresh with revoked token must fail
    refresh_res = await client.post(
        "/api/auth/refresh",
        json={"refreshToken": refresh_token},
    )
    assert refresh_res.status_code == 401
    assert refresh_res.json()["detail"] == "Refresh token has been revoked"

    # Duplicate logout with same revoked token must fail
    logout_again_res = await client.post(
        "/api/auth/logout",
        json={"refreshToken": refresh_token},
    )
    assert logout_again_res.status_code == 401
    assert (
        logout_again_res.json()["detail"]
        == "Refresh token has already been revoked"
    )


# 13. After 5 failed logins the 6th returns 429
async def test_rate_limiting_after_5_failed_logins(client: AsyncClient):
    await client.post(
        "/api/auth/signup",
        json={
            "name": "Rate Limit User",
            "email": "ratelimit@example.com",
            "password": "securepassword123",
        },
    )

    # Perform 5 failed login attempts
    for i in range(5):
        res = await client.post(
            "/api/auth/login",
            json={
                "email": "ratelimit@example.com",
                "password": "wrongpassword!",
            },
        )
        assert res.status_code == 401

    # The 6th login attempt must trigger rate limiting
    res_6th = await client.post(
        "/api/auth/login",
        json={
            "email": "ratelimit@example.com",
            "password": "securepassword123",
        },
    )
    assert res_6th.status_code == 429
    assert (
        res_6th.json()["detail"]
        == "Too many login attempts. Please try again later."
    )
