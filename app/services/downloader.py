"""Download service for VTH Music Bot."""
import asyncio
import os
from uuid import uuid4
from pathlib import Path
from app.utils.errors import DownloadError
import yt_dlp


# Temporary download directory
DOWNLOAD_DIR = Path(__file__).resolve().parents[2] / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Maximum download size (500 MB)
MAX_DOWNLOAD_SIZE = 500 * 1024 * 1024


async def download_audio(url: str, quality: str = "192") -> str | None:
    """Download audio from URL."""
    try:
        ydl_opts = {
            "format": "bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }],
            "quiet": True,
            "no_warnings": True,
            "outtmpl": str(DOWNLOAD_DIR / f"{uuid4().hex}_%(title)s.%(ext)s"),
            "max_filesize": MAX_DOWNLOAD_SIZE,
            "socket_timeout": 30,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(
                lambda: ydl.extract_info(url, download=True)
            )
            
            if info:
                filename = ydl.prepare_filename(info)
                # Change extension to mp3
                mp3_file = str(filename).rsplit(".", 1)[0] + ".mp3"
                if os.path.exists(mp3_file):
                    return mp3_file
        
        return None
    
    except Exception as e:
        raise DownloadError(f"Download failed: {str(e)}")


async def download_video(url: str, quality: str = "best") -> str | None:
    """Download video from URL."""
    try:
        ydl_opts = {
            "format": quality,
            "quiet": True,
            "no_warnings": True,
            "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
            "max_filesize": MAX_DOWNLOAD_SIZE,
            "socket_timeout": 30,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(
                lambda: ydl.extract_info(url, download=True)
            )
            
            if info:
                return ydl.prepare_filename(info)
        
        return None
    
    except Exception as e:
        raise DownloadError(f"Download failed: {str(e)}")


def cleanup_download(filepath: str):
    """Delete downloaded file."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass


def cleanup_all_downloads():
    """Delete all downloaded files."""
    try:
        for file in DOWNLOAD_DIR.glob("*"):
            if file.is_file():
                file.unlink()
    except Exception:
        pass
