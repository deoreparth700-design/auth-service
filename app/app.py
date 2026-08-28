from fastapi import FastAPI

from app.routes.auth_routes import router as auth_routes


app = FastAPI(
    title="Authentication API",
    description="Production-ready authentication service built with FastAPI and PostgreSQL",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "message": "Authentication API is running 🚀"
    }


app.include_router(
    auth_routes,
    prefix="/api/auth",
)