"""DJ user database operations."""
from app.database.client import get_database
from app.database.models import DJ


async def add_dj(group_id: int, user_id: int, added_by: int) -> bool:
    """Add a DJ to a group."""
    db = await get_database()
    
    existing = await db["djs"].find_one({
        "group_id": group_id,
        "user_id": user_id
    })
    
    if existing:
        return False
    
    dj = DJ(group_id=group_id, user_id=user_id, added_by=added_by)
    
    try:
        await db["djs"].insert_one(dj.dict())
        return True
    except Exception:
        return False


async def remove_dj(group_id: int, user_id: int) -> bool:
    """Remove a DJ from a group."""
    db = await get_database()
    
    result = await db["djs"].delete_one({
        "group_id": group_id,
        "user_id": user_id
    })
    
    return result.deleted_count > 0


async def is_dj(group_id: int, user_id: int) -> bool:
    """Check if user is a DJ in the group."""
    db = await get_database()
    
    dj = await db["djs"].find_one({
        "group_id": group_id,
        "user_id": user_id
    })
    
    return dj is not None


async def get_group_djs(group_id: int) -> list:
    """Get all DJs in a group."""
    db = await get_database()
    
    return await db["djs"].find({
        "group_id": group_id
    }).to_list(None)


async def get_group_dj_count(group_id: int) -> int:
    """Get number of DJs in a group."""
    db = await get_database()
    return await db["djs"].count_documents({"group_id": group_id})


async def clear_group_djs(group_id: int):
    """Remove all DJs from a group."""
    db = await get_database()
    await db["djs"].delete_many({"group_id": group_id})
