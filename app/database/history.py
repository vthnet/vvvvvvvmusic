"""Play history database operations."""
from datetime import datetime
from app.database.client import get_database
from app.database.models import HistoryEntry
from app.database.users import increment_user_history_count


async def add_to_history(user_id: int, title: str, artist: str, duration: int,
                         thumbnail: str = None, url: str = None) -> bool:
    """Add track to user history."""
    db = await get_database()
    
    entry = HistoryEntry(
        user_id=user_id,
        track_id=f"{title}:{artist}".lower(),
        title=title,
        artist=artist,
        duration=duration,
        thumbnail=thumbnail,
        url=url
    )
    
    try:
        await db["history"].insert_one(entry.dict())
        await increment_user_history_count(user_id, 1)
        return True
    except Exception:
        return False


async def get_user_history(user_id: int, skip: int = 0, limit: int = 50) -> list:
    """Get user's play history."""
    db = await get_database()
    
    return await db["history"].find(
        {"user_id": user_id}
    ).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)


async def get_user_history_count(user_id: int) -> int:
    """Get count of user's history entries."""
    db = await get_database()
    return await db["history"].count_documents({"user_id": user_id})


async def clear_user_history(user_id: int):
    """Clear all user history."""
    db = await get_database()
    
    count = await get_user_history_count(user_id)
    await db["history"].delete_many({"user_id": user_id})
    
    # Update user's history count
    db_inst = await get_database()
    await db_inst["users"].update_one(
        {"user_id": user_id},
        {"$set": {"history_count": 0}}
    )


async def update_play_duration(user_id: int, track_id: str, played_duration: int):
    """Update how long a track was played."""
    db = await get_database()
    
    await db["history"].update_one(
        {
            "user_id": user_id,
            "track_id": track_id,
            "timestamp": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
        },
        {"$set": {"played_duration": played_duration}},
        upsert=False
    )
