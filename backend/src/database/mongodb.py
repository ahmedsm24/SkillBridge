"""
MongoDB database configuration and connection management.
Provides secure connection handling with proper authentication.
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager with security features."""
    
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None
    gridfs: Optional[AsyncIOMotorGridFSBucket] = None
    
    @classmethod
    def get_connection_string(cls) -> str:
        """Build MongoDB connection string from environment variables."""
        host = os.getenv("MONGODB_HOST", "localhost")
        port = os.getenv("MONGODB_PORT", "27017")
        username = os.getenv("MONGODB_USERNAME", "")
        password = os.getenv("MONGODB_PASSWORD", "")
        database = os.getenv("MONGODB_DATABASE", "skillbridge")
        
        # Check for full connection string (e.g., MongoDB Atlas)
        full_uri = os.getenv("MONGODB_URI")
        if full_uri:
            return full_uri
        
        # Build connection string
        if username and password:
            return f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource=admin"
        else:
            return f"mongodb://{host}:{port}/{database}"
    
    @classmethod
    async def connect(cls) -> None:
        """Establish connection to MongoDB."""
        try:
            connection_string = cls.get_connection_string()
            database_name = os.getenv("MONGODB_DATABASE", "skillbridge")
            
            # Create client with security options
            cls.client = AsyncIOMotorClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                maxPoolSize=50,
                minPoolSize=10
            )
            
            # Verify connection
            await cls.client.admin.command('ping')
            
            cls.database = cls.client[database_name]
            cls.gridfs = AsyncIOMotorGridFSBucket(cls.database, bucket_name="resume_files")
            
            # Create indexes for better query performance
            await cls._create_indexes()
            
            logger.info(f"Connected to MongoDB database: {database_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def disconnect(cls) -> None:
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.database = None
            cls.gridfs = None
            logger.info("Disconnected from MongoDB")
    
    @classmethod
    async def _create_indexes(cls) -> None:
        """Create database indexes for performance and security."""
        if not cls.database:
            return
        
        # Resumes collection indexes
        await cls.database.resumes.create_index("created_at")
        await cls.database.resumes.create_index("filename")
        
        # Job descriptions collection indexes
        await cls.database.job_descriptions.create_index("created_at")
        await cls.database.job_descriptions.create_index("title")
        await cls.database.job_descriptions.create_index("domain")
        
        # Gap analyses collection indexes
        await cls.database.gap_analyses.create_index("resume_id")
        await cls.database.gap_analyses.create_index("job_description_id")
        await cls.database.gap_analyses.create_index("created_at")
        
        # Training modules collection indexes
        await cls.database.training_modules.create_index("resume_id")
        await cls.database.training_modules.create_index("gap_analysis_id")
        await cls.database.training_modules.create_index("created_at")
        await cls.database.training_modules.create_index("status")
        
        logger.info("Database indexes created")
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get the database instance."""
        if not cls.database:
            raise RuntimeError("Database not connected. Call connect() first.")
        return cls.database
    
    @classmethod
    def get_gridfs(cls) -> AsyncIOMotorGridFSBucket:
        """Get GridFS bucket for file storage."""
        if not cls.gridfs:
            raise RuntimeError("GridFS not initialized. Call connect() first.")
        return cls.gridfs


# Dependency for FastAPI
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get database instance."""
    return MongoDB.get_database()


async def get_gridfs() -> AsyncIOMotorGridFSBucket:
    """FastAPI dependency to get GridFS instance."""
    return MongoDB.get_gridfs()

