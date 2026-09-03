# Put your values directly here. No emoji .env registry is used.
import os
from dotenv import load_dotenv
load_dotenv()

def _parse_int(value: str, default: int = 0, name: str = "value") -> int:
    """Safely parse an integer value from environment variable."""
    if not value or value.startswith("PUT_"):
        return default
    try:
        return int(value)
    except ValueError:
        print(f"⚠️  Warning: {name} '{value}' is not a valid number, using {default}")
        return default

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = _parse_int(os.getenv("API_ID", "0"), 0, "API_ID")
API_HASH = os.getenv("API_HASH", "")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
OWNER_ID = _parse_int(os.getenv("OWNER_ID", "0"), 0, "OWNER_ID")
STRING_SESSION = os.getenv("STRING_SESSION", "")
SESSION_STRING = STRING_SESSION
GENIUS_API_KEY = os.getenv("GENIUS_API_KEY", "")

LINKS = {
    "privacy": "https://t.me/valriks",
    "policy": "https://t.me/valriks",
    "network": "https://t.me/valriks",
    "created_by": "https://t.me/valriks",
}

BUTTON_EMOJI = {
    "add": "4956368289371522616",
    "privacy": "6129579597441801084",
    "network": "6129433877791382400",
    "help": "6136308217761766184",
    "created_by": "5420560761221039711",
    "previous": "5255703720078879038",
    "pause": "5042036407137207122",
    "resume": "5208607440878197365",
    "next": "5253767677670862169",
    "loop": "5256110612395605858",
    "autoplay": "5278573677900752088",
    "shuffle": "5253464392850221514",
    "favorite": "5276239041052828276",
    "queue": "5258500400918587241",
    "replay": "5346269127059196142",
    "play_favorites": "5208607440878197365",
    "remove_favorite": "6129486856212979482",
    "download": "5255934767844567828",
    "close": "5974083768233760323",
}

