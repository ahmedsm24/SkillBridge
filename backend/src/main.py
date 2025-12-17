"""
Main FastAPI application for SkillBridge.
AI-powered system that analyzes resumes and generates personalized training modules.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import os
import logging

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Determine which database to use
USE_MONGODB = os.getenv("USE_MONGODB", "false").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    if USE_MONGODB:
        from src.database.mongodb import MongoDB
        logger.info("Connecting to MongoDB...")
        await MongoDB.connect()
        logger.info("MongoDB connected successfully")
    else:
        # SQLite fallback - create tables
        from src.database.models import Base
        from src.database.database import engine
        Base.metadata.create_all(bind=engine)
        logger.info("SQLite database initialized")
    
    yield
    
    # Shutdown
    if USE_MONGODB:
        from src.database.mongodb import MongoDB
        await MongoDB.disconnect()
        logger.info("MongoDB disconnected")


app = FastAPI(
    title="SkillBridge",
    description="AI-powered system that analyzes resumes, identifies skill gaps, and generates personalized training modules",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

# In production, be strict about origins. In development, allow all.
if os.getenv("ENVIRONMENT", "development") == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include appropriate router based on database choice
if USE_MONGODB:
    from src.api.mongo_routes import router
    logger.info("Using MongoDB routes")
else:
    from src.api.routes import router
    logger.info("Using SQLite routes")

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with application info."""
    return {
        "name": "SkillBridge",
        "description": "Resume-to-Training Module Generator",
        "version": "1.0.0",
        "status": "operational",
        "database": "mongodb" if USE_MONGODB else "sqlite"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "mongodb" if USE_MONGODB else "sqlite"
    }
    
    # Check database connection if using MongoDB
    if USE_MONGODB:
        try:
            from src.database.mongodb import MongoDB
            await MongoDB.client.admin.command('ping')
            health_status["database_status"] = "connected"
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["database_status"] = f"error: {str(e)}"
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
