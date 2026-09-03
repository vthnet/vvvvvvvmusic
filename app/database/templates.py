"""Persistent message templates configured by the bot owner."""
from datetime import datetime

from app.database.client import get_database


async def get_message_template(kind: str) -> str | None:
    """Return a saved HTML template, if one exists."""
    db = await get_database()
    document = await db["message_templates"].find_one({"kind": kind})
    if not document:
        return None
    return document.get("html") or ""


async def set_message_template(kind: str, html: str):
    """Save or replace an HTML message template."""
    db = await get_database()
    await db["message_templates"].update_one(
        {"kind": kind},
        {"$set": {"html": html, "updated_at": datetime.utcnow()}},
        upsert=True,
    )


async def delete_message_template(kind: str):
    """Remove a saved message template."""
    db = await get_database()
    await db["message_templates"].delete_one({"kind": kind})
