from app import config


DEFAULT_BUTTON_TEXT = {
    "previous": "⏮",
    "pause": "⏸",
    "resume": "▶",
    "next": "⏭",
    "loop": "🔁",
    "autoplay": "⚡",
    "shuffle": "🔀",
    "favorite": "❤",
    "queue": "☰",
    "replay": "↺",
    "download": "⬇",
    "close": "✕",
    "help": "❔",
    "add": "＋",
    "privacy": "🔒",
    "policy": "📄",
    "network": "🌐",
    "created_by": "✨",
}


def button(text, callback_data=None, url=None, icon_custom_emoji_id=None, emoji_key=None,
        disabled=False, icon_only=False, style="primary"):
    label = "\u2063" if icon_only else str(text or "•").strip() or "•"
    b = {"text": label}
    b["style"] = style
    if callback_data is not None:
        b["callback_data"] = callback_data
    if url is not None:
        b["url"] = url
    emoji_id = icon_custom_emoji_id or config.BUTTON_EMOJI.get(emoji_key)
    if emoji_id:
        b["icon_custom_emoji_id"] = emoji_id
    if disabled:
        b["disabled"] = True
    return b


def home_keyboard():
    return {
        "inline_keyboard": [
            [
                button("Add in Group", url="https://t.me/your_bot?startgroup=true", emoji_key="add")
            ],
                [button("Privacy", url=config.LINKS["privacy"], emoji_key="privacy"),
    
                button("Network", url=config.LINKS["network"], emoji_key="network"),
            ],
            [
                button("Help", callback_data="help", emoji_key="help"),
                button("Created By", url=config.LINKS["created_by"], emoji_key="created_by"),
            ],
            [
                button("My Favorites", callback_data="favorites:list", emoji_key="favorite"),
            ],
        ]
    }


def favorites_keyboard(favorites, page=1, per_page=10):
    total_pages = max((len(favorites) + per_page - 1) // per_page, 1)
    start = (page - 1) * per_page
    rows = [[
            button("Play Favorites", callback_data="favorites:playall", emoji_key="play_favorites", style="success"),
        button("Loop All", callback_data="favorites:loopall", emoji_key="loop", style="success"),
    ]]
    for favorite in favorites[start:start + per_page]:
        track_id = str(favorite.get("track_id", ""))
        title = str(favorite.get("title", "Untitled"))[:24]
        rows.append([
            button(title, callback_data=f"favorites:play:{track_id}"),
                button(
                    "Remove", callback_data=f"favorites:remove:{track_id}",
                    emoji_key="remove_favorite", style="danger"
                ),
        ])
    if total_pages > 1:
        navigation = []
        if page > 1:
            navigation.append(button("Previous", callback_data=f"favorites:page:{page - 1}"))
        if page < total_pages:
            navigation.append(button("Next", callback_data=f"favorites:page:{page + 1}"))
        rows.append(navigation)
    return {"inline_keyboard": rows}


def player_keyboard(chat_id, paused=False, autoplay=False, shuffle=False, loop="off"):
    mid = "resume" if paused else "pause"
    
    return {
        "inline_keyboard": [
            [
                button(DEFAULT_BUTTON_TEXT["previous"], f"player:previous:{chat_id}", emoji_key="previous", icon_only=True),
                button(DEFAULT_BUTTON_TEXT[mid], f"player:{mid}:{chat_id}", emoji_key=mid, icon_only=True),
                button(DEFAULT_BUTTON_TEXT["next"], f"player:next:{chat_id}", emoji_key="next", icon_only=True),
            ],
            [
                button(DEFAULT_BUTTON_TEXT["loop"], f"player:loop:{chat_id}", emoji_key="loop", icon_only=True),
                button(DEFAULT_BUTTON_TEXT["autoplay"], f"player:autoplay:{chat_id}", emoji_key="autoplay", icon_only=True),
                button(DEFAULT_BUTTON_TEXT["shuffle"], f"player:shuffle:{chat_id}", emoji_key="shuffle", icon_only=True),
            ],
            [
                button(DEFAULT_BUTTON_TEXT["favorite"], f"player:favorite:{chat_id}", emoji_key="favorite", icon_only=True),
                button(DEFAULT_BUTTON_TEXT["queue"], f"player:queue:{chat_id}", emoji_key="queue", icon_only=True),
                button(DEFAULT_BUTTON_TEXT["replay"], f"player:replay:{chat_id}", emoji_key="replay", icon_only=True),
            ],
            [
                button(DEFAULT_BUTTON_TEXT["close"], f"player:close:{chat_id}", emoji_key="close", icon_only=True),
            ],
        ]
    }
