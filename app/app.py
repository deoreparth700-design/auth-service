from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes.auth_routes import router as auth_routes


app = FastAPI()


# Serve frontend files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
async def root():
    return FileResponse("frontend/login.html")


@app.get("/login.html")
async def login_page():
    return FileResponse("frontend/login.html")


@app.get("/signup.html")
async def signup_page():
    return FileResponse("frontend/signup.html")


@app.get("/dashboard.html")
async def dashboard_page():
    return FileResponse("frontend/dashboard.html")


app.include_router(auth_routes, prefix="/api/auth")