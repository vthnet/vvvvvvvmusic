"""Shared yt-dlp configuration for YouTube requests."""
import base64
import logging
import os
import tempfile
from pathlib import Path


LOGGER = logging.getLogger(__name__)
COOKIE_FILE = Path(tempfile.gettempdir()) / "vth_youtube_cookies.txt"
_cookie_source: tuple[str, str] | None = None
_cookie_file: str | None = None


def get_youtube_cookie_file() -> str | None:
    """Materialize configured YouTube cookies and return their local path."""
    global _cookie_source, _cookie_file

    cookies_b64 = os.getenv("YOUTUBE_COOKIES_B64", "").strip()
    if cookies_b64:
        source = ("base64", cookies_b64)
        if source == _cookie_source and _cookie_file and COOKIE_FILE.is_file():
            return _cookie_file

        try:
            encoded = "".join(cookies_b64.split())
            cookie_data = base64.b64decode(encoded, validate=True)
            if not cookie_data:
                raise ValueError("empty cookie data")

            COOKIE_FILE.write_bytes(cookie_data)
            try:
                os.chmod(COOKIE_FILE, 0o600)
            except OSError:
                pass

            _cookie_source = source
            _cookie_file = str(COOKIE_FILE)
            LOGGER.info("YouTube cookies loaded from YOUTUBE_COOKIES_B64.")
            return _cookie_file
        except (OSError, ValueError):
            _cookie_source = source
            _cookie_file = None
            LOGGER.warning("YouTube cookie configuration is invalid.")
            return None

    cookie_path = os.getenv("YOUTUBE_COOKIES", "").strip()
    source = ("path", cookie_path)
    if cookie_path and Path(cookie_path).is_file():
        if source != _cookie_source:
            _cookie_source = source
            _cookie_file = cookie_path
            LOGGER.info("YouTube cookies loaded from YOUTUBE_COOKIES.")
        return cookie_path

    if source != _cookie_source:
        _cookie_source = source
        _cookie_file = None
        LOGGER.info("YouTube cookies are not configured; continuing without authenticated cookies.")
    return None


def youtube_ydl_opts(extra_options: dict | None = None) -> dict:
    """Build yt-dlp options with optional shared YouTube authentication."""
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": 30,
    }

    cookie_file = get_youtube_cookie_file()
    if cookie_file:
        options["cookiefile"] = cookie_file

    if extra_options:
        options.update(extra_options)
    return options