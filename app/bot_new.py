"""
Main bot file for VTH Music Bot - Professional Telegram music player
"""
import asyncio
import json
from html import escape
from typing import Optional
from datetime import datetime

import yt_dlp
from pyrogram import Client, enums, filters, idle
import pyrogram.errors as pyrogram_errors
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

# PyTgCalls compatibility
if not hasattr(pyrogram_errors, "GroupcallForbidden"):
    pyrogram_errors.GroupcallForbidden = pyrogram_errors.GroupCallInvalid
if not hasattr(pyrogram_errors, "GroupcallInvalid"):
    pyrogram_errors.GroupcallInvalid = pyrogram_errors.GroupCallInvalid

from pytgcalls import PyTgCalls
from pytgcalls import filters as call_filters
from pytgcalls.types import AudioQuality, GroupCallConfig, MediaStream, StreamEnded

# App imports
from app import config
from app.handlers.start import send_home, snap_video_path, to_pyrogram_keyboard
from app.player.state import PlayerManager
from app.utils.logger import bot_logger, playback_logger, error_logger, log_command, log_error
from app.utils.permissions import is_owner, is_group_admin, is_dj_or_admin, can_control_player, can_change_settings
from app.utils.helpers import safe_escape, format_duration, get_user_label, is_youtube_url
from app.ui.buttons import player_keyboard, home_keyboard
from app.ui.messages import player_text, search_results_text, queue_text, favorites_text, history_text
from app.services.search import search_youtube, get_track_info
from app.services.lyrics import get_lyrics
from app.services.youtube import youtube_ydl_opts
from app.services.telegram_api import TelegramAPI
from app.database.client import get_database, DatabaseClient
from app.database.users import get_or_create_user, get_user_count, block_user, unblock_user, get_all_users
from app.database.groups import get_or_create_group, get_group_count, get_or_create_group_settings
from app.database.favorites import add_favorite, remove_favorite, is_favorite, get_user_favorites
from app.database.history import add_to_history, get_user_history, clear_user_history
from app.database.dj import add_dj, remove_dj, is_dj, get_group_djs
from app.database.statistics import record_statistics, get_statistics_summary


def _user_label(user) -> str:
    """Get user display label."""
    if not user:
        return "Unknown user"
    if hasattr(user, 'username') and user.username:
        return f"@{user.username}"
    return " ".join(
        part for part in [getattr(user, 'first_name', None), getattr(user, 'last_name', None)] if part
    ) or str(getattr(user, 'id', 'Unknown'))


class MusicBot:
    def __init__(self, token: str | None = None):
        """Initialize the music bot."""
        self.bot_app = Client(
            "vth_music_bot",
            api_id=int(config.API_ID),
            api_hash=config.API_HASH,
            bot_token=token or config.BOT_TOKEN,
            in_memory=True,
        )
        self.user_app = Client(
            "vth_music_user",
            api_id=int(config.API_ID),
            api_hash=config.API_HASH,
            session_string=config.STRING_SESSION,
        )
        self.call = PyTgCalls(self.user_app)
        self.players = PlayerManager()
        self.queue_lock = asyncio.Lock()
        self.player_messages = {}
        self.player_message_modes = {}
        self.search_callback_data = {}  # Store search results for callback handling

    async def initialize(self):
        """Initialize bot connections and database."""
        try:
            db_client = DatabaseClient()
            await db_client.connect()
            bot_logger.info("Database connected successfully")
        except Exception as e:
            error_logger.error(f"Database connection failed: {e}")
            raise

    async def _download_metadata(self, query: str) -> dict:
        """Download track metadata using yt-dlp."""
        ydl_opts = youtube_ydl_opts({
            "skip_download": True,
            "extract_flat": False,
            "default_search": "ytsearch",
            "format": "bestaudio/best",
        })
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(lambda: ydl.extract_info(query, download=False))
                
                if not info:
                    raise ValueError("No music found")
                
                if info.get("_type") == "playlist":
                    info = info["entries"][0]
                if info.get("entries"):
                    info = info["entries"][0]
                
                if not info:
                    raise ValueError("No music found")
                
                title = info.get("title") or "VTH Music"
                audio_url = info.get("url")
                
                if not audio_url:
                    formats = info.get("formats") or []
                    audio_formats = [
                        f for f in formats
                        if f.get("acodec") not in (None, "none")
                        and f.get("vcodec") in (None, "none")
                    ]
                    if not audio_formats:
                        raise ValueError("No playable audio stream")
                    
                    audio_formats.sort(
                        key=lambda f: (f.get("tbr") or 0, f.get("quality") or ""),
                        reverse=True
                    )
                    audio_url = audio_formats[0].get("url") or info.get("webpage_url")
                
                return {
                    "title": title,
                    "url": audio_url,
                    "thumb": info.get("thumbnail"),
                    "duration": int(info.get("duration") or 0),
                    "artist": info.get("uploader") or info.get("channel") or "Unknown",
                    "genre": info.get("genre") or "",
                    "webpage_url": info.get("webpage_url"),
                }
        
        except Exception as e:
            log_error(e, "Metadata download failed")
            raise ValueError(f"Failed to get track: {str(e)}")

    async def _refresh_player(self, chat_id: int):
        """Refresh the player message with updated state."""
        message_id = self.player_messages.get(chat_id)
        state = self.players.get(chat_id)
        
        if not message_id or not state.current:
            return
        
        track = state.current
        duration = track.get("duration") or 0
        duration_text = format_duration(duration) if duration else "Live"
        
        text = player_text(
            title=track['title'],
            artist=track.get('artist', 'Unknown'),
            duration=duration,
            requested_by=track.get('requested_by', 'Unknown'),
            queue_waiting=max(len(state.queue) - state.current_index - 1, 0),
            paused=state.paused
        )
        
        markup = player_keyboard(
            chat_id,
            paused=state.paused,
            autoplay=state.autoplay,
            shuffle=state.shuffle,
            loop=state.loop
        )
        
        try:
            bot_api = TelegramAPI()
            try:
                if self.player_message_modes.get(chat_id) == "text":
                    await bot_api.edit_message_text(
                        chat_id, message_id, text, reply_markup=markup, parse_mode="HTML"
                    )
                else:
                    await bot_api.edit_message_caption(
                        chat_id, message_id, text, reply_markup=markup, parse_mode="HTML"
                    )
            finally:
                await bot_api.close()
        except Exception as e:
            log_error(e, "Player refresh failed")

    async def _play_next(self, chat_id: int):
        """Play next track in queue."""
        state = self.players.get(chat_id)
        
        if not state.queue:
            state.current = None
            state.current_index = -1
            playback_logger.info(f"Queue empty for chat {chat_id}")
            return
        
        # Handle loop one
        if state.loop == "one":
            # Replay current track
            if state.current:
                await self._play_real_track(
                    chat_id,
                    state.current["title"],
                    state.current["url"]
                )
            return
        
        # Move to next track
        if state.current is not None and state.queue:
            state.history.append(state.current)
            state.queue.pop(state.current_index)
        
        # Check if queue is empty
        if not state.queue:
            if state.autoplay and state.current:
                try:
                    # Generate recommendation query
                    recommendation_query = (
                        f"{state.current.get('artist', '')} "
                        f"{state.current.get('genre', '')} official audio"
                    ).strip()
                    
                    metadata = await self._download_metadata(f"ytsearch:{recommendation_query}")
                    
                    state.queue.append({
                        **metadata,
                        "requested_by": "Autoplay",
                    })
                
                except Exception as e:
                    log_error(e, "Autoplay failed")
                    state.current = None
                    state.current_index = -1
                    await self.bot_app.send_message(
                        chat_id,
                        "❌ Autoplay could not find another song."
                    )
                    return
            else:
                state.current = None
                state.current_index = -1
                await self.bot_app.send_message(
                    chat_id,
                    "📋 Queue finished. Add more songs with /play."
                )
                playback_logger.info(f"Queue finished for chat {chat_id}")
                return
        
        state.current_index = 0
        state.current = state.queue[0]
        
        await self._play_real_track(
            chat_id,
            state.current["title"],
            state.current["url"]
        )

    async def _on_stream_end(self, client, update):
        """Handle stream end event."""
        if update.stream_type & StreamEnded.Type.AUDIO:
            async with self.queue_lock:
                await self._play_next(update.chat_id)

    async def _shutdown(self):
        """Shutdown bot gracefully."""
        bot_logger.info("Shutting down bot...")
        
        for chat_id, state in list(self.players.states.items()):
            if state.current:
                try:
                    await self.call.leave_call(chat_id)
                except Exception:
                    pass
        
        if self.user_app.is_connected:
            await self.user_app.stop()
        if self.bot_app.is_connected:
            await self.bot_app.stop()
        
        bot_logger.info("Bot shutdown complete")

    async def _delete_message(self, message):
        """Delete a message safely."""
        try:
            await message.delete()
        except Exception:
            pass

    async def _send_loading(self, chat_id: int) -> Message | None:
        """Send loading message."""
        try:
            return await self.bot_app.send_message(
                chat_id,
                "⏳ <b>Preparing your track...</b>",
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception:
            return None

    async def _play_real_track(self, chat_id: int, title: str, url: str):
        """Start playback of a track."""
        if not url:
            raise ValueError("No playable URL found")
        
        try:
            stream = MediaStream(url, audio_parameters=AudioQuality.HIGH)
            state = self.players.get(chat_id)
            track = state.current or {}
            
            video_path = snap_video_path()
            duration = track.get("duration") or 0
            duration_text = format_duration(duration) if duration else "Live"
            
            caption = player_text(
                title=title,
                artist=track.get('artist', 'Unknown'),
                duration=duration,
                requested_by=track.get('requested_by', 'Unknown'),
                queue_waiting=max(len(state.queue) - state.current_index - 1, 0),
                paused=state.paused
            )
            
            markup = player_keyboard(
                chat_id,
                paused=state.paused,
                autoplay=state.autoplay,
                shuffle=state.shuffle,
                loop=state.loop
            )
            
            # Delete old player message
            old_message_id = self.player_messages.get(chat_id)
            if old_message_id:
                try:
                    await self.bot_app.delete_messages(chat_id, old_message_id)
                except Exception:
                    pass
            
            async def start_voice():
                await self.call.play(
                    chat_id,
                    stream,
                    config=GroupCallConfig(auto_start=True),
                )
            
            async def send_player_post():
                try:
                    bot_api = TelegramAPI()
                    try:
                        if video_path:
                            result = await bot_api.send_video(
                                chat_id, video_path, caption=caption,
                                reply_markup=markup, parse_mode="HTML"
                            )
                        else:
                            result = await bot_api.send_message(
                                chat_id, caption, reply_markup=markup, parse_mode="HTML"
                            )
                    finally:
                        await bot_api.close()

                    player_message_id = result["message_id"]
                    self.player_messages[chat_id] = player_message_id
                    self.player_message_modes[chat_id] = "caption" if video_path else "text"
                    
                    try:
                        await self.bot_app.pin_chat_message(
                            chat_id, player_message_id, disable_notification=True
                        )
                    except Exception:
                        pass
                
                except Exception as e:
                    log_error(e, f"Failed to send player post for {chat_id}")
            
            await asyncio.gather(start_voice(), send_player_post())
            playback_logger.info(f"Started playing: {title} in chat {chat_id}")
        
        except Exception as e:
            log_error(e, f"Playback failed for: {title}")
            await self.bot_app.send_message(
                chat_id,
                f"❌ <b>Playback error:</b> {safe_escape(str(e)[:100])}",
                parse_mode=enums.ParseMode.HTML
            )

    async def _queue_or_play(self, chat_id: int, query: str, requested_by: str = "Unknown"):
        """Add to queue or play immediately."""
        try:
            metadata = await self._download_metadata(query)
            state = self.players.get(chat_id)
            
            # Add to database
            await add_to_history(
                chat_id,
                metadata["title"],
                metadata.get("artist", "Unknown"),
                metadata.get("duration", 0),
                metadata.get("thumb"),
                query
            )
            
            state.queue.append({
                "title": metadata["title"],
                "url": metadata["url"],
                "thumb": metadata.get("thumb"),
                "query": query,
                "duration": metadata.get("duration", 0),
                "artist": metadata.get("artist", "Unknown"),
                "genre": metadata.get("genre", ""),
                "webpage_url": metadata.get("webpage_url"),
                "requested_by": requested_by,
            })
            
            # If nothing is playing, start playback
            if state.current is None:
                state.current = state.queue[0]
                state.current_index = 0
                await self._play_real_track(chat_id, metadata["title"], metadata["url"])
                return
            
            # Otherwise, notify about queue position
            position = len(state.queue) - state.current_index
            duration_text = format_duration(metadata.get("duration", 0))
            
            await self.bot_app.send_message(
                chat_id,
                f"✅ <b>Added to queue</b> at position <b>#{position}</b>\n\n"
                f"🎵 <b>{safe_escape(metadata['title'])}</b>\n"
                f"👤 {safe_escape(metadata.get('artist', 'Unknown'))}\n"
                f"⏱ {duration_text}",
                parse_mode=enums.ParseMode.HTML,
            )
        
        except Exception as e:
            log_error(e, f"Queue failed for query: {query}")
            raise

    async def _handle_message(self, client: Client, message: Message):
        """Handle incoming messages."""
        client_id = getattr(getattr(client, "me", None), "id", None)
        if (
            not message.text
            or getattr(message, "outgoing", False)
            or (message.from_user and message.from_user.id == client_id)
        ):
            return
        
        text = message.text.strip()
        command = text.split(maxsplit=1)[0].split("@", 1)[0].lower()
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else None
        
        try:
            # Register user and group
            if message.from_user:
                await get_or_create_user(
                    user_id,
                    message.from_user.first_name,
                    message.from_user.last_name,
                    message.from_user.username
                )
            
            if chat_id < 0:  # Group/channel
                await get_or_create_group(chat_id)
            
            # Delete command message
            await self._delete_message(message)
            
            # Check if it's a plain text search
            plain_play = text[5:].strip() if text.lower().startswith("play ") else None
            
            # Determine if it's a control command
            control_commands = (
                text.startswith("/play")
                or text.startswith("/queue")
                or text.startswith("/pause")
                or text.startswith("/resume")
                or text.startswith("/skip")
                or text.startswith("/stop")
                or plain_play is not None
                or (not text.startswith("/"))
            )
            
            # Check permissions
            if control_commands and chat_id < 0:  # Only check in groups
                can_play = await can_control_player(self.bot_app, chat_id, user_id)
                if not can_play:
                    await self.bot_app.send_message(
                        chat_id,
                        "❌ Only group admins/DJs can control music."
                    )
                    log_command(user_id, chat_id, "control_denied")
                    return
            
            # Command handling
            if command in {"/start", "/help"}:
                await send_home(
                    self.bot_app,
                    chat_id,
                    message.from_user.first_name if message.from_user else "there",
                )
                log_command(user_id, chat_id, "/start")
                return
            
            if text.startswith("/play") or plain_play is not None:
                query = text[5:].strip() if plain_play is None else plain_play
                if not query:
                    await self.bot_app.send_message(
                        chat_id,
                        "📝 <b>Usage:</b> /play <song name or YouTube link>",
                        parse_mode=enums.ParseMode.HTML
                    )
                    return
                
                loading = await self._send_loading(chat_id)
                try:
                    await self._queue_or_play(chat_id, query, _user_label(message.from_user))
                    log_command(user_id, chat_id, f"/play {query}", success=True)
                except Exception as e:
                    await self.bot_app.send_message(
                        chat_id,
                        f"❌ <b>Error:</b> {safe_escape(str(e)[:100])}",
                        parse_mode=enums.ParseMode.HTML
                    )
                    log_command(user_id, chat_id, f"/play {query}", success=False)
                finally:
                    if loading:
                        await self._delete_message(loading)
                return
            
            if text.startswith("/queue"):
                await self.bot_app.send_message(
                    chat_id,
                    queue_text(self.players.get(chat_id).queue, self.players.get(chat_id).current_index),
                    parse_mode=enums.ParseMode.HTML,
                )
                log_command(user_id, chat_id, "/queue")
                return
            
            if text.startswith("/pause"):
                await self.call.pause(chat_id)
                state = self.players.get(chat_id)
                state.paused = True
                await self.bot_app.send_message(
                    chat_id,
                    f"⏸ <b>Paused by {_user_label(message.from_user)}</b>",
                    parse_mode=enums.ParseMode.HTML
                )
                await self._refresh_player(chat_id)
                log_command(user_id, chat_id, "/pause")
                return
            
            if text.startswith("/resume"):
                await self.call.resume(chat_id)
                state = self.players.get(chat_id)
                state.paused = False
                await self.bot_app.send_message(
                    chat_id,
                    f"▶️ <b>Resumed by {_user_label(message.from_user)}</b>",
                    parse_mode=enums.ParseMode.HTML
                )
                await self._refresh_player(chat_id)
                log_command(user_id, chat_id, "/resume")
                return
            
            if text.startswith("/skip"):
                async with self.queue_lock:
                    state = self.players.get(chat_id)
                    if not state.current:
                        await self.bot_app.send_message(chat_id, "❌ Nothing is playing.")
                        return
                    
                    state.loop = "off"
                    await self._play_next(chat_id)
                
                await self.bot_app.send_message(
                    chat_id,
                    f"⏭ <b>Skipped by {_user_label(message.from_user)}</b>",
                    parse_mode=enums.ParseMode.HTML
                )
                log_command(user_id, chat_id, "/skip")
                return
            
            if text.startswith("/stop"):
                await self.call.leave_call(chat_id)
                state = self.players.get(chat_id)
                state.queue.clear()
                state.current = None
                state.current_index = -1
                self.player_messages.pop(chat_id, None)
                self.player_message_modes.pop(chat_id, None)
                
                await self.bot_app.send_message(
                    chat_id,
                    f"⏹ <b>Stopped by {_user_label(message.from_user)}</b>",
                    parse_mode=enums.ParseMode.HTML
                )
                log_command(user_id, chat_id, "/stop")
                return
            
            if text.startswith("/"):
                await self.bot_app.send_message(
                    chat_id,
                    f"❌ Command not supported: <b>{safe_escape(text)}</b>",
                    parse_mode=enums.ParseMode.HTML
                )
                return
            
            # Plain text search
            loading = await self._send_loading(chat_id)
            try:
                await self._queue_or_play(chat_id, text, _user_label(message.from_user))
                log_command(user_id, chat_id, f"text_search: {text}", success=True)
            except Exception as e:
                await self.bot_app.send_message(
                    chat_id,
                    f"❌ <b>Error:</b> {safe_escape(str(e)[:100])}",
                    parse_mode=enums.ParseMode.HTML
                )
                log_command(user_id, chat_id, f"text_search: {text}", success=False)
            finally:
                if loading:
                    await self._delete_message(loading)
        
        except Exception as e:
            log_error(e, f"Message handler failed for chat {chat_id}")

    async def _handle_callback(self, client: Client, callback: CallbackQuery):
        """Handle callback queries."""
        if not callback.data or not callback.data.startswith("player:"):
            return
        
        try:
            parts = callback.data.split(":", 2)
            if len(parts) < 3:
                return
            
            action = parts[1]
            chat_id = int(parts[2])
            actor = _user_label(callback.from_user)
            state = self.players.get(chat_id)
            
            # Permission check
            user_id = callback.from_user.id if callback.from_user else None
            can_act = await can_control_player(self.bot_app, chat_id, user_id)
            
            if not can_act:
                await callback.answer(
                    "❌ Only admins/DJs can control the player.",
                    show_alert=True
                )
                return
            
            # Handle actions
            if action == "pause":
                if not state.paused:
                    await self.call.pause(chat_id)
                    state.paused = True
                    await self._refresh_player(chat_id)
                    await callback.answer(f"⏸ Paused by {actor}")
                else:
                    await callback.answer("Already paused")
                return
            
            elif action == "resume":
                if state.paused:
                    await self.call.resume(chat_id)
                    state.paused = False
                    await self._refresh_player(chat_id)
                    await callback.answer(f"▶️ Resumed by {actor}")
                else:
                    await callback.answer("Already playing")
                return
            
            elif action == "next":
                async with self.queue_lock:
                    await self._play_next(chat_id)
                current_title = state.current.get("title", "Nothing queued") if state.current else "Nothing queued"
                await callback.answer(f"⏭ Skipped by {actor}: {current_title}")
                return
            
            elif action == "previous":
                if state.history:
                    state.current = state.history.pop()
                    if state.queue and state.current_index > 0:
                        state.queue[state.current_index - 1] = state.current
                    else:
                        state.queue.insert(0, state.current)
                    
                    await self._play_real_track(
                        chat_id,
                        state.current["title"],
                        state.current["url"]
                    )
                    await callback.answer(f"⏮ Previous by {actor}")
                else:
                    await callback.answer("No previous track")
                return
            
            elif action == "shuffle":
                state.toggle_shuffle(chat_id)
                status = "ON" if state.shuffle else "OFF"
                await callback.answer(f"🔀 Shuffle: {status}")
                await self._refresh_player(chat_id)
                return
            
            elif action == "loop":
                state.cycle_loop(chat_id)
                loop_text = {"off": "OFF", "one": "ONE", "all": "ALL"}[state.loop]
                await callback.answer(f"🔁 Loop: {loop_text}")
                await self._refresh_player(chat_id)
                return
            
            elif action == "autoplay":
                state.toggle_autoplay(chat_id)
                status = "ON" if state.autoplay else "OFF"
                await callback.answer(f"⚡ Autoplay: {status}")
                await self._refresh_player(chat_id)
                return
            
            elif action == "queue":
                await self.bot_app.send_message(
                    chat_id,
                    queue_text(state.queue, state.current_index),
                    parse_mode=enums.ParseMode.HTML
                )
                await callback.answer("Queue opened")
                return
            
            elif action == "close":
                await self.call.leave_call(chat_id)
                state.queue.clear()
                state.current = None
                state.current_index = -1
                self.player_messages.pop(chat_id, None)
                self.player_message_modes.pop(chat_id, None)
                
                await callback.answer("Player closed")
                return
            
            elif action == "replay":
                if state.current:
                    await self._play_real_track(
                        chat_id,
                        state.current["title"],
                        state.current["url"]
                    )
                    await callback.answer("Replay started")
                else:
                    await callback.answer("No track to replay")
                return
            
            elif action == "download":
                url = state.current.get("webpage_url") if state.current else None
                if url:
                    await self.bot_app.send_message(chat_id, url, disable_web_page_preview=True)
                    await callback.answer("Source link sent")
                else:
                    await callback.answer("Source link unavailable")
                return
            
            elif action == "favorite":
                if state.current:
                    is_fav = await is_favorite(
                        user_id,
                        state.current["title"],
                        state.current["artist"]
                    )
                    
                    if is_fav:
                        await callback.answer("Already in favorites")
                    else:
                        await add_favorite(
                            user_id,
                            state.current["title"],
                            state.current.get("artist", "Unknown"),
                            state.current.get("duration", 0),
                            state.current.get("thumb")
                        )
                        await callback.answer("❤️ Added to favorites")
                else:
                    await callback.answer("No track playing")
                return
            
            await callback.answer("Unknown action")
        
        except Exception as e:
            log_error(e, "Callback handler failed")
            await callback.answer(f"Error: {str(e)[:50]}", show_alert=True)

    async def run(self):
        """Run the bot."""
        if not config.BOT_TOKEN:
            raise RuntimeError("BOT_TOKEN is required")
        
        if not config.STRING_SESSION:
            raise RuntimeError("STRING_SESSION is required")
        
        bot_logger.info("🎵 VTH MUSIC BOT STARTING...")
        
        # Initialize database
        await self.initialize()
        
        # Register handlers
        @self.bot_app.on_message(
            filters.command(["start", "help", "play", "queue", "pause", "resume", "skip", "stop"])
        )
        async def on_command(client: Client, message: Message):
            try:
                await self._handle_message(client, message)
            except Exception as e:
                log_error(e, "Command handler error")
                await self.bot_app.send_message(
                    message.chat.id,
                    f"❌ <b>Error:</b> {safe_escape(str(e)[:100])}",
                    parse_mode=enums.ParseMode.HTML
                )
        
        @self.bot_app.on_message(filters.text & ~filters.command([
            "start", "help", "play", "queue", "pause", "resume", "skip", "stop"
        ]))
        async def on_text(client: Client, message: Message):
            try:
                await self._handle_message(client, message)
            except Exception as e:
                log_error(e, "Text handler error")
        
        @self.bot_app.on_callback_query(filters.regex(r"^player:"))
        async def on_callback(client: Client, callback: CallbackQuery):
            try:
                await self._handle_callback(client, callback)
            except Exception as e:
                log_error(e, "Callback handler error")
        
        @self.call.on_update(call_filters.stream_end(StreamEnded.Type.AUDIO))
        async def on_stream_end(client, update):
            try:
                await self._on_stream_end(client, update)
            except Exception as e:
                log_error(e, "Stream end handler error")
        
        try:
            await self.bot_app.start()
            await self.user_app.start()
            await self.call.start()
            
            bot_logger.info("✅ VTH MUSIC BOT STARTED SUCCESSFULLY")
            bot_logger.info("Bot is running and listening for commands...")
            
            await idle()
        
        finally:
            await self._shutdown()


async def main():
    """Main entry point."""
    try:
        bot = MusicBot()
        await bot.run()
    except Exception as e:
        error_logger.critical(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
