"""YouTube search and metadata extraction service."""
import asyncio

import yt_dlp

from app.services.youtube import youtube_ydl_opts
from app.utils.errors import SearchError


async def search_youtube(query: str, max_results: int = 5) -> list:
    """Search YouTube and return source metadata only, never an expiring media URL."""
    try:
        ydl_opts = youtube_ydl_opts({
            "skip_download": True,
            "extract_flat": True,
            "default_search": "ytsearch",
            "playlistend": max_results,
        })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(
                lambda: ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            )

        if not info or not info.get("entries"):
            raise SearchError("No results found")

        results = []
        for entry in info["entries"][:max_results]:
            if not entry:
                continue

            video_id = entry.get("id") or ""
            webpage_url = entry.get("webpage_url") or (
                f"https://www.youtube.com/watch?v={video_id}" if video_id else ""
            )
            if not webpage_url:
                continue

            results.append({
                "video_id": video_id,
                "id": video_id,
                "title": entry.get("title", "Unknown"),
                "artist": entry.get("uploader", "Unknown"),
                "duration": int(entry.get("duration") or 0),
                "thumbnail": entry.get("thumbnail", ""),
                "webpage_url": webpage_url,
                "source_url": webpage_url,
                "url": webpage_url,
                "view_count": int(entry.get("view_count") or 0),
            })

        if not results:
            raise SearchError("No playable results found")

        return results

    except SearchError:
        raise
    except Exception as exc:
        raise SearchError(f"Search failed: {exc}") from exc


async def get_track_info(query: str) -> dict:
    """Get detailed track information while storing source metadata, not a temporary stream URL."""
    try:
        ydl_opts = youtube_ydl_opts({
            "skip_download": True,
            "extract_flat": False,
            "default_search": "ytsearch",
        })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(
                lambda: ydl.extract_info(query, download=False)
            )

        if not info:
            raise SearchError("No information found")

        if info.get("_type") == "playlist":
            entries = info.get("entries") or []
            if not entries:
                raise SearchError("No information found")
            info = entries[0]
        elif info.get("entries"):
            entries = info["entries"]
            if not entries:
                raise SearchError("No information found")
            info = entries[0]

        if not info:
            raise SearchError("No information found")

        video_id = info.get("id") or ""
        webpage_url = info.get("webpage_url") or (
            f"https://www.youtube.com/watch?v={video_id}" if video_id else ""
        )

        if not webpage_url:
            raise SearchError("No playable source URL available")

        return {
            "title": info.get("title", "Unknown"),
            "video_id": video_id,
            "id": video_id,
            "artist": info.get("uploader", info.get("channel", "Unknown")),
            "duration": int(info.get("duration", 0) or 0),
            "thumbnail": info.get("thumbnail", ""),
            "webpage_url": webpage_url,
            "source_url": webpage_url,
            "url": webpage_url,
            "genre": info.get("genre", ""),
            "view_count": int(info.get("view_count") or 0),
            "upload_date": info.get("upload_date", ""),
        }

    except SearchError:
        raise
    except Exception as exc:
        raise SearchError(f"Failed to get track info: {exc}") from exc


async def is_video_available(url: str) -> bool:
    """Check if video is available for playback."""
    try:
        ydl_opts = youtube_ydl_opts({
            "skip_download": True,
        })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(
                lambda: ydl.extract_info(url, download=False)
            )

        return info is not None and "id" in info
    except Exception:
        return False
