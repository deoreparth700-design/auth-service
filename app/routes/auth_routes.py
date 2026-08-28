from fastapi import APIRouter

from app.controllers.auth_controller import (
    signup,
    login,
    get_me,
    refresh_access_token,
    logout,
    SignupRequest,
    LoginRequest,
    RefreshTokenRequest,
    LogoutRequest,
)

router = APIRouter()

router.add_api_route(
    "/signup",
    signup,
    methods=["POST"],
)

router.add_api_route(
    "/login",
    login,
    methods=["POST"],
)

router.add_api_route(
    "/me",
    get_me,
    methods=["GET"],
)

router.add_api_route(
    "/refresh",
    refresh_access_token,
    methods=["POST"],
)

router.add_api_route(
    "/logout",
    logout,
    methods=["POST"],
)