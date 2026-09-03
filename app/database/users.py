"""User database operations."""
from datetime import datetime
from app.database.client import get_database
from app.database.models import User


async def get_or_create_user(user_id: int, first_name: str = None, last_name: str = None, 
                             username: str = None) -> dict:
    """Get or create a user."""
    db = await get_database()
    
    existing = await db["users"].find_one({"user_id": user_id})
    if existing:
        await db["users"].update_one(
            {"user_id": user_id},
            {"$set": {"last_active": datetime.utcnow()}}
        )
        return existing
    
    user = User(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        username=username
    )
    result = await db["users"].insert_one(user.dict())
    return await db["users"].find_one({"_id": result.inserted_id})


async def get_user(user_id: int) -> dict | None:
    """Get user by ID."""
    db = await get_database()
    return await db["users"].find_one({"user_id": user_id})


async def block_user(user_id: int):
    """Block a user from using the bot."""
    db = await get_database()
    await db["users"].update_one(
        {"user_id": user_id},
        {"$set": {"is_blocked": True}}
    )


async def unblock_user(user_id: int):
    """Unblock a user."""
    db = await get_database()
    await db["users"].update_one(
        {"user_id": user_id},
        {"$set": {"is_blocked": False}}
    )


async def is_user_blocked(user_id: int) -> bool:
    """Check if user is blocked."""
    db = await get_database()
    user = await db["users"].find_one({"user_id": user_id})
    return user.get("is_blocked", False) if user else False


async def get_user_count() -> int:
    """Get total user count."""
    db = await get_database()
    return await db["users"].count_documents({})


async def get_all_users(skip: int = 0, limit: int = 100) -> list:
    """Get paginated list of users."""
    db = await get_database()
    return await db["users"].find().skip(skip).limit(limit).to_list(limit)


async def increment_user_favorite_count(user_id: int, increment: int = 1):
    """Increment user's favorite count."""
    db = await get_database()
    await db["users"].update_one(
        {"user_id": user_id},
        {"$inc": {"favorite_count": increment}}
    )


async def increment_user_history_count(user_id: int, increment: int = 1):
    """Increment user's history count."""
    db = await get_database()
    await db["users"].update_one(
        {"user_id": user_id},
        {"$inc": {"history_count": increment}}
    )
