from html import escape
from pathlib import Path

from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import inspect

from app import config
from app.ui.messages import bot_api_html, home_text
from app.ui.buttons import home_keyboard, player_keyboard
from app.services.telegram_api import TelegramAPI


def snap_video_path(index: int | None = None):
    snaps_dir = Path(__file__).resolve().parents[2] / "assets" / "snaps"
    videos = sorted(snaps_dir.glob("*.mp4"))
    if not videos:
        return None
    if index is None:
        import random
        return str(random.choice(videos))
    return str(videos[index % len(videos)])


async def send_home(api, chat_id, name="there", text=None, entities=None):
    keyboard = home_keyboard()
    text = text or home_text(name)
    if api.__class__.__module__.startswith("pyrogram"):
        bot_api = TelegramAPI()
        try:
            return await bot_api.send_message(
                chat_id, bot_api_html(text), reply_markup=keyboard, parse_mode="HTML"
            )
        finally:
            await bot_api.close()
    return await api.send_message(
        chat_id,
        text,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML if entities is None else None,
    )


def to_pyrogram_keyboard(keyboard):
    supports_custom_emoji = "icon_custom_emoji_id" in inspect.signature(InlineKeyboardButton).parameters
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                **{
                    "text": item["text"],
                    "callback_data": item.get("callback_data"),
                    "url": item.get("url"),
                    **({"icon_custom_emoji_id": item["icon_custom_emoji_id"]}
                       if supports_custom_emoji and item.get("icon_custom_emoji_id") else {}),
                }
            )
            for item in row
        ]
        for row in keyboard["inline_keyboard"]
    ])


async def send_player_post(api, chat_id, title="VTH Music", artist="Premium Mix", snap_video=None):
    selected = snap_video or snap_video_path()
    safe_title = escape(str(title))
    safe_artist = escape(str(artist))
    caption = (
        f"<b>{safe_title}</b>\n"
        f"<blockquote>{safe_artist}</blockquote>\n\n"
        f"<b>Play mode:</b> Premium snap card • Live queue ready"
    )
    markup = player_keyboard(chat_id)
    parse_mode = "HTML"
    if api.__class__.__module__.startswith("pyrogram"):
        bot_api = TelegramAPI()
        try:
            return await bot_api.send_video(
                chat_id, selected, caption=bot_api_html(caption),
                reply_markup=markup, parse_mode=parse_mode,
            )
        finally:
            await bot_api.close()
    return await api.send_video(
        chat_id,
        selected,
        caption=caption,
        reply_markup=markup,
        parse_mode=parse_mode,
    )
