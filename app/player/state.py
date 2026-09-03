from dataclasses import dataclass, field
from html import escape
from typing import Any
import random


@dataclass
class PlayerState:
    chat_id: int
    paused: bool = False
    autoplay: bool = False
    shuffle: bool = False
    loop: str = "off"  # off, one, favorites, all
    volume: int = 100
    queue: list[dict[str, Any]] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    current: dict[str, Any] | None = None
    current_index: int = -1
    current_search_results: list[dict[str, Any]] = field(default_factory=list)
    current_search_page: int = 1


class PlayerManager:
    def __init__(self):
        self.states = {}

    def get(self, chat_id):
        return self.states.setdefault(chat_id, PlayerState(chat_id))

    def add_track(self, chat_id, title, audio_url=None, video_url=None, **kwargs):
        state = self.get(chat_id)
        track = {
            "title": title,
            "audio_url": audio_url,
            "video_url": video_url,
            **kwargs,
        }
        if "webpage_url" not in track and "url" in kwargs:
            track["webpage_url"] = kwargs["url"]
        state.queue.append(track)
        if state.current is None and state.queue:
            state.current = state.queue[0]
            state.current_index = 0
        return state

    def set_current(self, chat_id, index):
        state = self.get(chat_id)
        if not state.queue:
            state.current = None
            state.current_index = -1
            return state
        state.current_index = max(0, min(index, len(state.queue) - 1))
        state.current = state.queue[state.current_index]
        return state

    def next_track(self, chat_id):
        state = self.get(chat_id)
        if not state.queue:
            return state
        if state.current_index >= len(state.queue) - 1:
            if state.loop == "all":
                state.current_index = 0
            else:
                state.current_index = len(state.queue) - 1
        else:
            state.current_index += 1
        state.current = state.queue[state.current_index]
        return state

    def previous_track(self, chat_id):
        state = self.get(chat_id)
        if not state.queue:
            return state
        if state.current_index <= 0:
            state.current_index = 0
        else:
            state.current_index -= 1
        state.current = state.queue[state.current_index]
        return state

    def toggle_pause(self, chat_id):
        s = self.get(chat_id)
        s.paused = not s.paused
        return s

    def toggle_autoplay(self, chat_id):
        s = self.get(chat_id)
        s.autoplay = not s.autoplay
        return s

    def toggle_shuffle(self, chat_id):
        s = self.get(chat_id)
        s.shuffle = not s.shuffle
        if s.shuffle and s.queue and len(s.queue) > 1:
            # Shuffle only future songs, keep current
            future = s.queue[s.current_index + 1:]
            random.shuffle(future)
            s.queue = s.queue[:s.current_index + 1] + future
        return s

    def cycle_loop(self, chat_id, favorites_available=False):
        s = self.get(chat_id)
        if s.loop == "off":
            s.loop = "one"
        elif s.loop == "one":
            s.loop = "favorites" if favorites_available else "off"
        elif s.loop == "favorites":
            s.loop = "all" if favorites_available else "off"
        else:
            s.loop = "off"
        return s

    def set_volume(self, chat_id, volume: int):
        s = self.get(chat_id)
        s.volume = max(0, min(100, volume))
        return s

    def remove_track(self, chat_id, index: int) -> bool:
        state = self.get(chat_id)
        if not (0 <= index < len(state.queue)):
            return False
        
        state.queue.pop(index)
        
        # Adjust current_index if necessary
        if index < state.current_index:
            state.current_index -= 1
        elif index == state.current_index:
            if state.current_index >= len(state.queue):
                state.current_index = max(0, len(state.queue) - 1)
            
            if state.queue:
                state.current = state.queue[state.current_index]
            else:
                state.current = None
                state.current_index = -1
        
        return True

    def clear_queue(self, chat_id):
        state = self.get(chat_id)
        state.queue.clear()
        state.current = None
        state.current_index = -1
        return state

    def set_search_results(self, chat_id, results: list):
        state = self.get(chat_id)
        state.current_search_results = results
        state.current_search_page = 1
        return state

    def move_track(self, chat_id, from_index: int, to_index: int) -> bool:
        state = self.get(chat_id)
        if not (0 <= from_index < len(state.queue) and 0 <= to_index < len(state.queue)):
            return False
        
        track = state.queue.pop(from_index)
        state.queue.insert(to_index, track)
        
        # Adjust current_index
        if from_index == state.current_index:
            state.current_index = to_index
        elif from_index < state.current_index <= to_index:
            state.current_index -= 1
        elif to_index <= state.current_index < from_index:
            state.current_index += 1
        
        state.current = state.queue[state.current_index] if state.queue else None
        return True

    def queue_summary(self, chat_id):
        state = self.get(chat_id)
        if not state.queue:
            return "Queue is empty. Use /play <song_name> to add the first track."
        lines = []
        for index, item in enumerate(state.queue[:8], start=1):
            prefix = "▶" if index - 1 == state.current_index else "•"
            title = escape(str(item.get('title', 'Untitled track')))
            duration = int(item.get("duration") or 0)
            duration_text = f"{duration // 60}:{duration % 60:02d}" if duration else "Live"
            requested_by = escape(str(item.get("requested_by") or "Unknown user"))
            lines.append(
                f"{prefix} {index}. <b>{title}</b>\n"
                f"<blockquote>Duration: {duration_text}\n"
                f"Requested by: {requested_by}</blockquote>"
            )
        return "<b>Queue</b>\n" + "\n".join(lines)

    def current_title(self, chat_id):
        state = self.get(chat_id)
        if not state.current:
            return "No track playing"
        return state.current.get("title", "Untitled track")

