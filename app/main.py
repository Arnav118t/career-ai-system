from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Career AI - Placement Decision Support",
        "version": "1.0.0"
    }