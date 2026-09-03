"""Lyrics service for VTH Music Bot."""
import asyncio
from app.utils.errors import VTHMusicException


class LyricsProvider:
    """Abstract lyrics provider."""
    
    async def get_lyrics(self, title: str, artist: str) -> str | None:
        """Get lyrics for a song."""
        raise NotImplementedError


class GeniusLyricsProvider(LyricsProvider):
    """Genius lyrics provider."""
    
    async def get_lyrics(self, title: str, artist: str) -> str | None:
        """Get lyrics from Genius."""
        try:
            # For now, return None - can be integrated with Genius API
            # Requires: pip install lyricsgenius
            return None
        except Exception:
            return None


class LocalLyricsCache:
    """Simple local lyrics cache."""
    
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str) -> str | None:
        """Get cached lyrics."""
        return self._cache.get(key)
    
    def set(self, key: str, lyrics: str):
        """Cache lyrics."""
        self._cache[key] = lyrics
    
    def clear(self):
        """Clear cache."""
        self._cache.clear()


# Global cache
_cache = LocalLyricsCache()
_provider = GeniusLyricsProvider()


async def get_lyrics(title: str, artist: str) -> str | None:
    """Get lyrics for a song."""
    try:
        cache_key = f"{title}:{artist}".lower()
        
        # Check cache
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached if cached else None
        
        # Try provider
        lyrics = await _provider.get_lyrics(title, artist)
        
        # Cache result
        _cache.set(cache_key, lyrics or "")
        
        return lyrics
    
    except Exception:
        return None


def set_lyrics_provider(provider: LyricsProvider):
    """Set custom lyrics provider."""
    global _provider
    _provider = provider


def clear_lyrics_cache():
    """Clear lyrics cache."""
    _cache.clear()
