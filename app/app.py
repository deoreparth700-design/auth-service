from fastapi import FastAPI

from app.routes.auth_routes import router as auth_routes

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Authentication API is running 🚀"}


app.include_router(auth_routes, prefix="/api/auth")
