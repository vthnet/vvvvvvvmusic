"""MongoDB client initialization and management."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app import config


class DatabaseClient:
    """Manages MongoDB connection and database access."""
    
    _instance = None
    _db: AsyncIOMotorDatabase | None = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self) -> AsyncIOMotorDatabase:
        """Initialize MongoDB connection."""
        if self._db is None:
            if not config.MONGO_URI:
                raise RuntimeError("MONGO_URI environment variable is not set")
            
            client = AsyncIOMotorClient(config.MONGO_URI)
            self._db = client["vth_music_bot"]
            
            # Create indexes
            await self._create_indexes()
        
        return self._db
    
    async def _create_indexes(self):
        """Create database indexes for performance."""
        try:
            # Users collection indexes
            await self._db["users"].create_index("user_id", unique=True)
            await self._db["users"].create_index("created_at")
            
            # Groups collection indexes
            await self._db["groups"].create_index("group_id", unique=True)
            await self._db["groups"].create_index("created_at")
            
            # Favorites collection indexes
            await self._db["favorites"].create_index([("user_id", 1), ("track_id", 1)], unique=True)
            await self._db["favorites"].create_index("user_id")
            
            # History collection indexes
            await self._db["history"].create_index("user_id")
            await self._db["history"].create_index("timestamp")
            await self._db["history"].create_index([("user_id", 1), ("timestamp", -1)])
            
            # Settings collection indexes
            await self._db["settings"].create_index("group_id", unique=True)
            
            # DJ collection indexes
            await self._db["djs"].create_index([("group_id", 1), ("user_id", 1)], unique=True)
            await self._db["djs"].create_index("group_id")
            
            # Statistics collection indexes
            await self._db["statistics"].create_index("timestamp")
            
        except Exception as e:
            print(f"Error creating indexes: {e}")
    
    async def disconnect(self):
        """Close MongoDB connection."""
        if self._db is not None:
            self._db.client.close()
            self._db = None
    
    async def get_db(self) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if self._db is None:
            await self.connect()
        return self._db


async def get_database() -> AsyncIOMotorDatabase:
    """Get or create database instance."""
    client = DatabaseClient()
    return await client.get_db()
