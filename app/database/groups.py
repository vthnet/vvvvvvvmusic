"""Group database operations."""
from datetime import datetime
from app.database.client import get_database
from app.database.models import Group, GroupSettings


async def get_or_create_group(group_id: int, title: str = None) -> dict:
    """Get or create a group."""
    db = await get_database()
    
    existing = await db["groups"].find_one({"group_id": group_id})
    if existing:
        return existing
    
    group = Group(group_id=group_id, title=title)
    result = await db["groups"].insert_one(group.dict())
    return await db["groups"].find_one({"_id": result.inserted_id})


async def get_group(group_id: int) -> dict | None:
    """Get group by ID."""
    db = await get_database()
    return await db["groups"].find_one({"group_id": group_id})


async def get_group_count() -> int:
    """Get total group count."""
    db = await get_database()
    return await db["groups"].count_documents({})


async def set_group_active(group_id: int, is_active: bool = True):
    """Set group active status."""
    db = await get_database()
    await db["groups"].update_one(
        {"group_id": group_id},
        {"$set": {"is_active": is_active}}
    )


async def get_or_create_group_settings(group_id: int) -> dict:
    """Get or create group settings."""
    db = await get_database()
    
    existing = await db["settings"].find_one({"group_id": group_id})
    if existing:
        return existing
    
    settings = GroupSettings(group_id=group_id)
    result = await db["settings"].insert_one(settings.dict())
    return await db["settings"].find_one({"_id": result.inserted_id})


async def get_group_settings(group_id: int) -> dict | None:
    """Get group settings."""
    db = await get_database()
    return await db["settings"].find_one({"group_id": group_id})


async def update_group_settings(group_id: int, **kwargs):
    """Update group settings."""
    db = await get_database()
    kwargs["updated_at"] = datetime.utcnow()
    await db["settings"].update_one(
        {"group_id": group_id},
        {"$set": kwargs},
        upsert=True
    )


async def get_group_volume(group_id: int) -> int:
    """Get group default volume."""
    settings = await get_or_create_group_settings(group_id)
    return settings.get("default_volume", 100)


async def set_group_volume(group_id: int, volume: int):
    """Set group default volume."""
    await update_group_settings(group_id, default_volume=max(0, min(100, volume)))
