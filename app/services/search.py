"""YouTube search and metadata extraction service."""
import asyncio
from app.utils.errors import SearchError
from app.services.youtube import youtube_ydl_opts
import yt_dlp


async def search_youtube(query: str, max_results: int = 5) -> list:
    """Search YouTube and return results."""
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
                
                result = {
                    "id": entry.get("id", ""),
                    "title": entry.get("title", "Unknown"),
                    "artist": entry.get("uploader", "Unknown"),
                    "duration": entry.get("duration", 0),
                    "thumbnail": entry.get("thumbnail", ""),
                    "url": entry.get("url", ""),
                    "webpage_url": entry.get("webpage_url", ""),
                    "view_count": entry.get("view_count", 0),
                }
                
                if result["url"]:
                    results.append(result)
            
            if not results:
                raise SearchError("No playable results found")
            
            return results
    
    except SearchError:
        raise
    except Exception as e:
        raise SearchError(f"Search failed: {str(e)}")


async def get_track_info(query: str) -> dict:
    """Get detailed track information."""
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
                info = info.get("entries", [{}])[0]
            elif info.get("entries"):
                info = info["entries"][0]
            
            if not info:
                raise SearchError("No information found")
            
            # Extract audio URL
            audio_url = info.get("url")
            if not audio_url:
                formats = info.get("formats", [])
                audio_formats = [
                    f for f in formats
                    if f.get("acodec") not in (None, "none")
                    and f.get("vcodec") in (None, "none")
                ]
                
                if not audio_formats:
                    raise SearchError("No playable audio stream available")
                
                audio_formats.sort(
                    key=lambda f: (f.get("tbr", 0), f.get("quality", "")),
                    reverse=True
                )
                audio_url = audio_formats[0].get("url") or info.get("webpage_url")
            
            return {
                "title": info.get("title", "Unknown"),
                "artist": info.get("uploader", info.get("channel", "Unknown")),
                "duration": int(info.get("duration", 0)),
                "thumbnail": info.get("thumbnail", ""),
                "url": audio_url,
                "webpage_url": info.get("webpage_url", ""),
                "genre": info.get("genre", ""),
                "view_count": info.get("view_count", 0),
                "upload_date": info.get("upload_date", ""),
            }
    
    except SearchError:
        raise
    except Exception as e:
        raise SearchError(f"Failed to get track info: {str(e)}")


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
