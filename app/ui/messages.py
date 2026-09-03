from html import escape
import re
from pyrogram.parser.html import HTML

from app.utils.helpers import format_duration

POWERED_BY = '<a href="https://t.me/vthchannel">ᴠᴛʜ • ɴᴇᴛᴡᴏʀᴋ</a>'


def render_template(template: str, values: dict[str, object]) -> str:
    """Replace supported placeholders while leaving Telegram HTML untouched."""
    for key, value in values.items():
        template = template.replace("{" + key + "}", str(value))
    return template


def pyrogram_html(html: str) -> str:
    """Normalize saved custom emoji tags for Pyrogram HTML parsing."""
    return re.sub(
        r'<tg-emoji\s+emoji-id="([^"]+)">(.*?)</tg-emoji>',
        r'<emoji id="\1">\2</emoji>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )


def bot_api_html(html: str) -> str:
    """Normalize Pyrogram emoji tags for Bot API HTML parsing."""
    return re.sub(
        r'<emoji\s+id="([^"]+)">(.*?)</emoji>',
        r'<tg-emoji emoji-id="\1">\2</tg-emoji>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )


async def telegram_payload(html: str) -> tuple[str, list[dict]]:
    """Convert Bot API HTML into plain text and native Telegram entities."""
    quote_modes = [
        bool(match.group(1))
        for match in re.finditer(r"<blockquote(\s+expandable)?\s*>", html, re.IGNORECASE)
    ]
    parser_html = pyrogram_html(html)
    parsed = await HTML(None).parse(parser_html)
    entities = []
    type_names = {
        "strike": "strikethrough",
        "blockquote": "blockquote",
        "expandableblockquote": "expandable_blockquote",
        "customemoji": "custom_emoji",
        "textlink": "text_link",
        "texturl": "text_link",
        "textmention": "text_mention",
        "inputmentionname": "text_link",
        "phonenumber": "phone_number",
    }
    quote_index = 0
    for entity in parsed.get("entities") or []:
        entity_type = entity.__class__.__name__.replace("MessageEntity", "").lower()
        entity_type = type_names.get(entity_type, entity_type)
        payload = {"type": entity_type, "offset": entity.offset, "length": entity.length}
        if entity_type == "blockquote":
            if quote_index < len(quote_modes) and quote_modes[quote_index]:
                payload["type"] = "expandable_blockquote"
            quote_index += 1
        for field in ("url", "language", "custom_emoji_id"):
            value = getattr(entity, field, None)
            if field == "custom_emoji_id" and not value:
                value = getattr(entity, "document_id", None)
            if value:
                payload[field] = str(value)
        if entity_type == "text_link" and not payload.get("url"):
            user_id = getattr(entity, "user_id", None)
            if user_id:
                payload["url"] = f"tg://user?id={user_id}"
        entities.append(payload)
    entities.sort(key=lambda entity: (entity["offset"], -entity["length"]))
    return parsed["message"], entities


def home_text(name="there"):
    safe_name = escape(str(name))
    return (
        f"🎵 <b>VTH MUSIC</b>\n\n"
        f"<blockquote>Premium music, clean controls and a faster player built for Telegram.</blockquote>\n\n"
        f"👋 Welcome, <b>{safe_name}</b>\n"
        f"🎧 Add me to a group and start playing.\n\n"
        f"<b>Fast • Stable • Ready to play</b>"
    )


def player_text(title: str, artist: str, duration: int, requested_by: str, 
                queue_waiting: int, paused: bool = False) -> str:
    """Generate player message text."""
    safe_title = escape(str(title))
    safe_artist = escape(str(artist))
    safe_requester = str(requested_by)
    duration_text = format_duration(duration) if duration else "Live"
    status = "⏸ PAUSED" if paused else "▶️ NOW PLAYING"
    
    return (
        f"🎵 <b>VTH MUSIC</b>\n\n"
        f"<b>{safe_title}</b>\n"
        f"<blockquote>👤 {safe_artist}\n"
        f"⏱ {duration_text}\n"
        f"📨 Requested by: {safe_requester}\n"
        f"📋 Queue: {queue_waiting} waiting</blockquote>\n\n"
        f"━━━━━━━━━━━━━━\n"
        f"<b>{status}</b>\n"
        f"━━━━━━━━━━━━━━"
    )


def search_results_text(query: str, results: list, page: int = 1, per_page: int = 5) -> str:
    """Generate search results message."""
    safe_query = escape(str(query))
    total_pages = (len(results) + per_page - 1) // per_page
    
    text = f"🔎 <b>Search Results</b>\n<b>Query:</b> {safe_query}\n\n"
    
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, len(results))
    
    for idx, result in enumerate(results[start_idx:end_idx], 1):
        safe_title = escape(str(result.get("title", "Unknown")))
        safe_artist = escape(str(result.get("artist", "Unknown")))
        duration = format_duration(result.get("duration", 0))
        
        text += f"{idx}. 🎵 <b>{safe_title}</b>\n"
        text += f"   👤 {safe_artist} • {duration}\n\n"
    
    text += f"<b>Page {page}/{total_pages}</b>"
    
    return text


def queue_text(queue_items: list, current_index: int = -1, page: int = 1, 
               per_page: int = 10) -> str:
    """Generate queue message."""
    if not queue_items:
        return "📋 <b>Queue</b>\n\nQueue is empty. Use /play to add songs."
    
    total_pages = (len(queue_items) + per_page - 1) // per_page
    
    text = f"📋 <b>Queue</b> ({len(queue_items)} songs)\n\n"
    
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, len(queue_items))
    
    total_queue_duration = 0
    
    for idx, item in enumerate(queue_items[start_idx:end_idx], start_idx + 1):
        safe_title = escape(str(item.get("title", "Untitled")))
        safe_artist = escape(str(item.get("artist", "Unknown")))
        duration = item.get("duration", 0)
        duration_text = format_duration(duration)
        total_queue_duration += duration
        
        prefix = "▶️" if idx - 1 == current_index else "•"
        text += f"{prefix} {idx}. <b>{safe_title}</b>\n"
        text += f"   {safe_artist} • {duration_text}\n\n"
    
    text += f"<b>Page {page}/{total_pages}</b>\n"
    text += f"Total duration: {format_duration(total_queue_duration)}"
    
    return text


def favorites_text(favorites: list, page: int = 1, per_page: int = 10) -> str:
    """Generate favorites message."""
    if not favorites:
        return "❤️ <b>My Favorites</b>\n\nNo favorites yet. Add songs with the ❤️ button."
    
    total_pages = (len(favorites) + per_page - 1) // per_page
    
    text = f"❤️ <b>My Favorites</b> ({len(favorites)} songs)\n\n"
    
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, len(favorites))
    
    for idx, fav in enumerate(favorites[start_idx:end_idx], start_idx + 1):
        safe_title = escape(str(fav.get("title", "Untitled")))
        safe_artist = escape(str(fav.get("artist", "Unknown")))
        duration = format_duration(fav.get("duration", 0))
        
        text += f"{idx}. 🎵 <b>{safe_title}</b>\n"
        text += f"   {safe_artist} • {duration}\n\n"
    
    text += f"<b>Page {page}/{total_pages}</b>"
    
    return text


def help_text() -> str:
    """Generate a compact categorized command and controls guide."""
    return (
        "❖ <b>VTH MUSIC HELP</b>\n\n"
        "<blockquote><b>PLAYBACK</b>\n"
        "/play &lt;song or link&gt; - Play or queue a song\n"
        "/queue - View the queue\n"
        "/pause /resume - Pause or continue\n"
        "/skip - Play the next track\n"
        "/stop - Stop and clear playback</blockquote>\n"
        "<blockquote><b>FAVORITES</b>\n"
        "/favorites - View your saved favorites\n"
        "/myfavourites - Queue and play favorites in a group\n"
        "❤️ Favorite button - Save the current song\n"
        "🗑 Remove - Delete a saved favorite</blockquote>\n"
        "<blockquote><b>PLAYER BUTTONS</b>\n"
        "⏮ ⏭ Previous / next\n"
        "🔁 Loop: this song, favorites, all songs, off\n"
        "⚡ Autoplay - Add random related songs\n"
        "🔀 Shuffle - Mix upcoming songs\n"
        "⬇ Download • ↺ Replay • ☰ Queue</blockquote>\n"
        "<blockquote><b>OWNER</b>\n"
        "/setstart, /setplayer - Save custom messages\n"
        "/setstartquote, /setplayerquote - Force a quote\n"
        "/resetstart, /resetplayer - Restore defaults</blockquote>"
    )


def history_text(history: list, page: int = 1, per_page: int = 10) -> str:
    """Generate history message."""
    if not history:
        return "📜 <b>Play History</b>\n\nNo history yet. Play some songs!"
    
    total_pages = (len(history) + per_page - 1) // per_page
    
    text = f"📜 <b>Play History</b> ({len(history)} songs)\n\n"
    
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, len(history))
    
    for idx, entry in enumerate(history[start_idx:end_idx], start_idx + 1):
        safe_title = escape(str(entry.get("title", "Untitled")))
        safe_artist = escape(str(entry.get("artist", "Unknown")))
        
        text += f"{idx}. 🎵 <b>{safe_title}</b>\n"
        text += f"   {safe_artist}\n\n"
    
    text += f"<b>Page {page}/{total_pages}</b>"
    
    return text


def lyrics_text(title: str, artist: str, lyrics: str) -> str:
    """Generate lyrics message."""
    safe_title = escape(str(title))
    safe_artist = escape(str(artist))
    
    text = f"🎤 <b>Lyrics</b>\n\n"
    text += f"<b>{safe_title}</b>\n"
    text += f"👤 {safe_artist}\n\n"
    text += f"<blockquote>{escape(lyrics)}</blockquote>"
    
    return text


def stats_text(stats: dict) -> str:
    """Generate statistics message."""
    text = (
        f"📊 <b>VTH MUSIC Statistics</b>\n\n"
        f"👥 <b>Users:</b> {stats.get('total_users', 0):,}\n"
        f"👥 <b>Groups:</b> {stats.get('total_groups', 0):,}\n"
        f"🎵 <b>Songs Played:</b> {stats.get('songs_played', 0):,}\n"
        f"🔎 <b>Searches:</b> {stats.get('searches_performed', 0):,}\n"
        f"📥 <b>Downloads:</b> {stats.get('downloads_completed', 0):,}\n"
        f"🎧 <b>Active Players:</b> {stats.get('active_players', 0)}\n\n"
        f"Total Listening Time: {format_duration(stats.get('total_listening_time', 0))}"
    )
    
    return text


def group_settings_text(settings: dict) -> str:
    """Generate group settings message."""
    music_status = "✅" if settings.get("music_enabled") else "❌"
    admin_only = "✅" if settings.get("admin_only_controls") else "❌"
    dj_mode = "✅" if settings.get("dj_mode") else "❌"
    autoplay = "✅" if settings.get("autoplay_enabled") else "❌"
    delete_cmds = "✅" if settings.get("delete_play_commands") else "❌"
    leave_empty = "✅" if settings.get("leave_when_empty") else "❌"
    
    text = (
        f"⚙️ <b>Group Settings</b>\n\n"
        f"🎧 Music Enabled: {music_status}\n"
        f"👑 Admin Only: {admin_only}\n"
        f"🎛 DJ Mode: {dj_mode}\n"
        f"⚡ Autoplay: {autoplay}\n"
        f"🗑 Delete Commands: {delete_cmds}\n"
        f"🚪 Leave When Empty: {leave_empty}\n\n"
        f"🔊 Default Volume: {settings.get('default_volume', 100)}%\n"
        f"🔁 Default Loop: {settings.get('default_loop', 'off')}\n"
        f"🌐 Language: {settings.get('language', 'en')}"
    )
    
    return text

