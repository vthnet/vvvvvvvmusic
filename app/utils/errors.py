"""Custom exceptions for VTH Music Bot."""


class VTHMusicException(Exception):
    """Base exception for VTH Music Bot."""
    pass


class PlaybackError(VTHMusicException):
    """Playback error."""
    pass


class DownloadError(VTHMusicException):
    """Download error."""
    pass


class StreamError(VTHMusicException):
    """Stream error."""
    pass


class DatabaseError(VTHMusicException):
    """Database error."""
    pass


class SearchError(VTHMusicException):
    """Search error."""
    pass


class ConfigError(VTHMusicException):
    """Configuration error."""
    pass
