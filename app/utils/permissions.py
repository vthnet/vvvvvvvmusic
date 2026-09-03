"""Permission system for VTH Music Bot."""
from app import config
from app.database.dj import is_dj
from app.database.groups import get_group_settings


async def is_owner(user_id: int) -> bool:
    """Check if user is bot owner."""
    return user_id == config.OWNER_ID


async def is_group_admin(app, chat_id: int, user_id: int) -> bool:
    """Check if user is group admin."""
    from pyrogram import enums
    
    try:
        chat = await app.get_chat(chat_id)
        if chat.type not in {enums.ChatType.GROUP, enums.ChatType.SUPERGROUP}:
            return True
        
        if not user_id:
            return False
        
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in {
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR,
        }
    except Exception:
        return False


async def is_dj_or_admin(app, chat_id: int, user_id: int) -> bool:
    """Check if user is DJ or group admin."""
    admin = await is_group_admin(app, chat_id, user_id)
    if admin:
        return True
    
    dj = await is_dj(chat_id, user_id)
    return dj


async def can_control_player(app, chat_id: int, user_id: int) -> bool:
    """Check if user can control player in group."""
    settings = await get_group_settings(chat_id)
    
    if not settings or not settings.get("admin_only_controls", False):
        return True
    
    if settings.get("dj_mode", False):
        return await is_dj_or_admin(app, chat_id, user_id)
    
    return await is_group_admin(app, chat_id, user_id)


async def can_add_dj(app, chat_id: int, user_id: int) -> bool:
    """Check if user can add DJs."""
    return await is_group_admin(app, chat_id, user_id)


async def can_change_settings(app, chat_id: int, user_id: int) -> bool:
    """Check if user can change group settings."""
    return await is_group_admin(app, chat_id, user_id)
