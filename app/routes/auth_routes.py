from fastapi import APIRouter

from app.controllers.auth_controller import (
    signup,
    login,
    SignupRequest,
    LoginRequest,
)

router = APIRouter()

router.add_api_route("/signup", signup, methods=["POST"])
router.add_api_route("/login", login, methods=["POST"])
