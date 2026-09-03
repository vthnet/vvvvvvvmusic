"""Statistics database operations."""
from datetime import datetime, timedelta
from app.database.client import get_database
from app.database.models import Statistics


async def record_statistics(total_users: int, total_groups: int, songs_played: int,
                           searches_performed: int, downloads_completed: int,
                           active_players: int, total_listening_time: int):
    """Record a statistics snapshot."""
    db = await get_database()
    
    stats = Statistics(
        total_users=total_users,
        total_groups=total_groups,
        songs_played=songs_played,
        searches_performed=searches_performed,
        downloads_completed=downloads_completed,
        active_players=active_players,
        total_listening_time=total_listening_time
    )
    
    await db["statistics"].insert_one(stats.dict())


async def get_latest_statistics() -> dict | None:
    """Get the most recent statistics snapshot."""
    db = await get_database()
    
    return await db["statistics"].find_one(
        sort=[("timestamp", -1)]
    )


async def get_statistics_range(hours: int = 24) -> list:
    """Get statistics from the last N hours."""
    db = await get_database()
    
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    return await db["statistics"].find(
        {"timestamp": {"$gte": cutoff}}
    ).sort("timestamp", -1).to_list(None)


async def get_statistics_summary() -> dict:
    """Get summary statistics."""
    db = await get_database()
    
    latest = await get_latest_statistics()
    
    if not latest:
        return {
            "total_users": 0,
            "total_groups": 0,
            "songs_played": 0,
            "searches_performed": 0,
            "downloads_completed": 0,
            "active_players": 0,
            "total_listening_time": 0,
            "timestamp": None
        }
    
    return latest
