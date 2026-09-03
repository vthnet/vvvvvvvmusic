"""Favorite tracks database operations."""
from hashlib import md5
from app.database.client import get_database
from app.database.models import Favorite
from app.database.users import increment_user_favorite_count


def _generate_track_id(title: str, artist: str) -> str:
    """Generate unique track ID from title and artist."""
    key = f"{title}:{artist}".lower()
    return md5(key.encode()).hexdigest()


async def add_favorite(user_id: int, title: str, artist: str, duration: int, 
                       thumbnail: str = None) -> bool:
    """Add track to user favorites."""
    db = await get_database()
    track_id = _generate_track_id(title, artist)
    
    favorite = Favorite(
        user_id=user_id,
        track_id=track_id,
        title=title,
        artist=artist,
        duration=duration,
        thumbnail=thumbnail
    )
    
    try:
        await db["favorites"].insert_one(favorite.dict())
        await increment_user_favorite_count(user_id, 1)
        return True
    except Exception:
        return False


async def remove_favorite(user_id: int, track_id: str) -> bool:
    """Remove track from user favorites."""
    db = await get_database()
    
    result = await db["favorites"].delete_one({
        "user_id": user_id,
        "track_id": track_id
    })
    
    if result.deleted_count > 0:
        await increment_user_favorite_count(user_id, -1)
        return True
    return False


async def is_favorite(user_id: int, title: str, artist: str) -> bool:
    """Check if track is in user favorites."""
    db = await get_database()
    track_id = _generate_track_id(title, artist)
    
    fav = await db["favorites"].find_one({
        "user_id": user_id,
        "track_id": track_id
    })
    return fav is not None


async def get_user_favorites(user_id: int, skip: int = 0, limit: int = 50) -> list:
    """Get user's favorite tracks."""
    db = await get_database()
    
    return await db["favorites"].find(
        {"user_id": user_id}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)


async def get_user_favorites_count(user_id: int) -> int:
    """Get count of user's favorites."""
    db = await get_database()
    return await db["favorites"].count_documents({"user_id": user_id})


async def clear_user_favorites(user_id: int):
    """Clear all user favorites."""
    db = await get_database()
    
    count = await get_user_favorites_count(user_id)
    await db["favorites"].delete_many({"user_id": user_id})
    await increment_user_favorite_count(user_id, -count)
