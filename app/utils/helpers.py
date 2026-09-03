"""Helper utilities for VTH Music Bot."""
from html import escape
import asyncio


def safe_escape(text: str | None) -> str:
    """Safely escape text for HTML."""
    if not text:
        return "Unknown"
    return escape(str(text)[:100])


def format_duration(seconds: int) -> str:
    """Format seconds to MM:SS or HH:MM:SS."""
    if seconds <= 0:
        return "0:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def get_user_label(user) -> str:
    """Get user display name."""
    if not user:
        return "Unknown user"
    
    if hasattr(user, 'username') and user.username:
        return f"@{user.username}"
    
    if hasattr(user, 'first_name') and user.first_name:
        parts = [user.first_name]
        if hasattr(user, 'last_name') and user.last_name:
            parts.append(user.last_name)
        return " ".join(parts)
    
    if hasattr(user, 'id'):
        return str(user.id)
    
    return str(user)


async def run_async_with_timeout(coro, timeout: int = 30):
    """Run async function with timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")


def is_youtube_url(url: str) -> bool:
    """Check if URL is YouTube URL."""
    return "youtube.com" in url or "youtu.be" in url
