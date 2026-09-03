"""Shared yt-dlp configuration for YouTube requests."""
import asyncio

import yt_dlp

from app.utils.logger import bot_logger


def youtube_ydl_opts(extra_options: dict | None = None) -> dict:
    """Build a shared yt-dlp configuration without cookie requirements."""
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": 30,
        "js_runtimes": {
            "deno": {},
        },
    }

    if extra_options:
        options.update(extra_options)

    return options


async def extract_audio_stream(source: str) -> dict:
    """Resolve a fresh direct audio URL from a YouTube source without downloading to disk."""
    if not source or not str(source).strip():
        raise ValueError("No YouTube source URL or ID provided")

    source_url = str(source).strip()
    bot_logger.info(f"[YT] Extracting fresh audio stream: {source_url}")

    try:
        ydl_opts = youtube_ydl_opts({
            "format": "bestaudio/best",
            "download": False,
            "extract_flat": False,
            "noplaylist": True,
        })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(
                lambda: ydl.extract_info(source_url, download=False)
            )

        if not info:
            raise ValueError("No audio stream found")

        if info.get("_type") == "playlist":
            entries = info.get("entries") or []
            if not entries:
                raise ValueError("No playlist entries available")
            info = entries[0]
        elif info.get("entries"):
            entries = info["entries"]
            if not entries:
                raise ValueError("No video entries available")
            info = entries[0]

        stream_url = info.get("url")
        if not stream_url:
            formats = info.get("formats") or []
            audio_formats = [
                f for f in formats
                if f.get("acodec") not in (None, "none")
                and f.get("vcodec") in (None, "none")
            ]
            if not audio_formats:
                raise ValueError("No playable audio stream available")
            audio_formats.sort(
                key=lambda f: (f.get("tbr") or 0, f.get("quality") or ""),
                reverse=True,
            )
            stream_url = audio_formats[0].get("url")

        if not stream_url:
            raise ValueError("yt-dlp did not return a direct audio URL")

        result = {
            "url": stream_url,
            "title": info.get("title") or "Unknown",
            "video_id": info.get("id") or "",
            "artist": info.get("uploader") or info.get("channel") or "Unknown",
            "duration": int(info.get("duration") or 0),
            "thumbnail": info.get("thumbnail") or "",
            "webpage_url": info.get("webpage_url") or source_url,
            "source_url": info.get("webpage_url") or source_url,
        }
        bot_logger.info(f"[YT] Fresh audio URL extracted for {result['video_id'] or source_url}")
        return result
    except Exception as exc:
        bot_logger.exception(f"[YT] Extraction failed for {source_url}: {exc}")
        raise