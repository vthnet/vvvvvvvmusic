"""Professional logging configuration for VTH Music Bot."""
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Create logs directory
LOGS_DIR = Path(__file__).resolve().parents[2] / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Logger configuration
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ConsoleFormatter(logging.Formatter):
    """Format records without failing on terminals with limited encodings."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        encoding = getattr(self, "_encoding", None) or "utf-8"
        return message.encode(encoding, errors="replace").decode(encoding, errors="replace")


def get_logger(name: str, log_file: str = "bot.log") -> logging.Logger:
    """Get or create a logger."""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    
    # File handler
    log_path = LOGS_DIR / log_file
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = ConsoleFormatter(LOG_FORMAT, LOG_DATE_FORMAT)
    console_formatter._encoding = getattr(console_handler.stream, "encoding", None)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


# Module-specific loggers
bot_logger = get_logger("bot", "bot.log")
playback_logger = get_logger("playback", "playback.log")
error_logger = get_logger("error", "errors.log")
admin_logger = get_logger("admin", "admin.log")


def log_command(user_id: int, chat_id: int, command: str, success: bool = True):
    """Log a command execution."""
    status = "✓" if success else "✗"
    admin_logger.info(f"{status} Command: {command} | User: {user_id} | Chat: {chat_id}")


def log_playback(chat_id: int, action: str, track: str = ""):
    """Log playback events."""
    playback_logger.info(f"Chat {chat_id}: {action} | {track}")


def log_error(error: Exception, context: str = ""):
    """Log errors professionally."""
    error_logger.error(f"{context}: {str(error)}", exc_info=True)
    bot_logger.error(f"{context}: {str(error)}")
