from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.routes.auth_routes import router as auth_routes

app = FastAPI()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/")
async def root():
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/dashboard.html")
async def dashboard():
    return FileResponse(FRONTEND_DIR / "dashboard.html")


app.include_router(auth_routes, prefix="/api/auth")