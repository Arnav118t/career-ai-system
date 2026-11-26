from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# API Routers
from app.api import auth_routes, profile_routes, offer_routes, recommendation_routes, resume_routes

# Database
from app.db.database import engine, Base

# Create tables
print("MAIN APP STARTED")
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Career AI - Placement Decision Support System",
    description="AI-powered career guidance for engineering students",
    version="1.0.0"
)

# Register API routers
app.include_router(auth_routes.router, prefix="/api")
app.include_router(profile_routes.router, prefix="/api")
app.include_router(offer_routes.router, prefix="/api")
app.include_router(recommendation_routes.router, prefix="/api")
app.include_router(resume_routes.router, prefix="/api")

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Health check
@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Career AI - Placement Decision Support",
        "version": "1.0.0"
    }