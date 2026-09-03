# VTH MUSIC Bot - Setup & Configuration Guide

## Quick Start

### Step 1: Get Telegram Credentials

#### A. Get Bot Token (BotFather)
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the wizard to create a bot
4. Copy the bot token (format: `123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz`)

#### B. Get API Credentials (my.telegram.org)
1. Go to https://my.telegram.org/
2. Login with your Telegram account
3. Click "API Development tools"
4. Create a new application or use existing one
5. Note your `API ID` (integer) and `API Hash` (string)

#### C. Get Your User ID
1. Search for `@userinfobot` on Telegram
2. Send any message to get your user ID
3. This is your `OWNER_ID`

### Step 2: Setup MongoDB

**Option A: Local MongoDB**
```bash
# Windows
# Download from https://www.mongodb.com/try/download/community
# Install with default settings
# Windows will auto-start MongoDB service on localhost:27017

# Linux
sudo apt-get install mongodb
sudo systemctl start mongodb

# macOS
brew install mongodb-community
brew services start mongodb-community
```

**Option B: MongoDB Atlas (Cloud)**
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Create database user with credentials
4. Whitelist your IP
5. Copy connection string (URI)

### Step 3: Generate Pyrogram Session

This creates a session string that allows the bot to join voice chats.

```bash
# Create virtual environment first
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install pyrogram temporarily
pip install pyrogram tgcrypto

# Generate session
python -m pyrogram create_session

# Follow prompts:
# - App API ID: <your API ID>
# - App API hash: <your API hash>
# - Phone number: <your phone number with country code>
# - Code (sent to Telegram): <enter code>
# - Password (if 2FA enabled): <your 2FA password>

# This creates vth_music_bot.session file
# Copy the session string and save it for .env file
```

### Step 4: Create .env File

```bash
# Copy template
cp .env.example .env

# Edit .env with your credentials
```

**Required Variables:**
```
BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz
API_ID=12345678
API_HASH=abcdefghijklmnopqrstuvwxyz123456
OWNER_ID=987654321
MONGO_URI=mongodb://localhost:27017
STRING_SESSION=BQA-... (from pyrogram session)
GENIUS_API_KEY=  # Optional, for lyrics
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Run Bot

```bash
python run.py
# or
python app/main.py
```

You should see:
```
🎵 VTH MUSIC BOT STARTING...
✅ VTH MUSIC BOT STARTED SUCCESSFULLY
Bot is running and listening for commands...
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'pyrogram'"
```bash
pip install pyrogram tgcrypto yt-dlp pytgcalls pymongo motor pydantic python-dotenv httpx
```

### "MongoDB connection failed"
- Check MongoDB is running: `mongod --version`
- Verify connection string in .env
- For Atlas, check IP whitelist and password

### "STRING_SESSION is required"
- Run `python -m pyrogram create_session` to generate session
- Verify the session string is in .env file

### "BOT_TOKEN is required"
- Check .env file has BOT_TOKEN set
- Verify token format from BotFather

### Bot starts but doesn't respond to commands
- Check bot is added to groups with admin rights
- Verify BOT_TOKEN is correct
- Check API_ID and API_HASH are correct
- Review logs in `logs/` directory

### Can't join voice chat
- Make sure STRING_SESSION is generated correctly
- Verify user account is not restricted by Telegram
- Check PyTgCalls is installed: `pip install py-tgcalls`

### Custom emojis not showing
- Edit `app/config.py` EMOJI dictionary
- Use emoji IDs from your Telegram app
- Fallback to Unicode emojis automatically if IDs are wrong

## Advanced Configuration

### Custom Emoji IDs

Edit `app/config.py`:
```python
EMOJI = {
    "default": "5359906629918854889",
    "play": "5359906629918854890",
    "pause": "5359906629918854891",
    # ... get IDs from https://www.emojitool.com/
}
```

### Logging Configuration

Logs are auto-created in `logs/` with:
- `bot.log` - General bot activity
- `playback.log` - Music playback events
- `errors.log` - Errors and exceptions
- `admin.log` - Admin actions

Change log level in `app/utils/logger.py` (line 20):
```python
logging.basicConfig(level=logging.DEBUG)  # or INFO, WARNING
```

### FFmpeg Installation

For download feature:
```bash
# Windows (with chocolatey)
choco install ffmpeg

# Linux
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Genius Lyrics API

1. Go to https://genius.com/api-clients
2. Create access token
3. Add to .env:
   ```
   GENIUS_API_KEY=your_token_here
   ```

## Project Structure

```
app/
├── bot.py              # Main bot class (MusicBot)
├── main.py             # Entry point
├── config.py           # Configuration
├── database/           # MongoDB operations
│   ├── client.py
│   ├── models.py
│   ├── users.py
│   ├── groups.py
│   ├── favorites.py
│   ├── history.py
│   ├── dj.py
│   └── statistics.py
├── services/           # External services
│   ├── search.py      # YouTube search
│   ├── lyrics.py      # Lyrics fetching
│   └── downloader.py  # Audio/video download
├── utils/              # Utilities
│   ├── logger.py      # Logging system
│   ├── permissions.py # Permission checking
│   ├── helpers.py     # Helper functions
│   ├── errors.py      # Custom exceptions
│   └── emoji.py       # Emoji registry
├── ui/                 # User interface
│   ├── buttons.py     # Keyboard layouts
│   └── messages.py    # Message templates
├── player/             # Player state
│   └── state.py       # PlayerManager
└── handlers/           # Command handlers
    └── start.py       # Home screen

logs/
├── bot.log
├── playback.log
├── errors.log
└── admin.log

downloads/              # Downloaded files
assets/
└── snaps/              # Video snap cards
```

## Commands Reference

### User Commands
- `/start` - Show home screen
- `/help` - Show help
- `/play <song>` - Play a song
- `/queue` - Show queue
- `/pause` - Pause player
- `/resume` - Resume player
- `/skip` - Skip track
- `/stop` - Stop player

### Player Buttons
| Button | Action |
|--------|--------|
| ⏮ | Previous track |
| ⏸/▶ | Pause/Resume |
| ⏭ | Next track |
| 🔁 | Loop (OFF→ONE→ALL) |
| ⚡ | Autoplay toggle |
| 🔀 | Shuffle toggle |
| ❤️ | Add to favorites |
| ☰ | View queue |
| ↺ | Replay current |
| ⬇️ | Download track |
| ❌ | Close player |

## Performance Tips

1. **Use MongoDB Atlas** for better performance than local MongoDB
2. **Enable indexes** - Done automatically on first run
3. **Set log level to INFO** for production (less disk I/O)
4. **Use SSD** for better database performance
5. **Monitor RAM** - Each active player stream uses ~50MB

## Security

- Never commit .env file to version control
- Store BOT_TOKEN securely
- Rotate API keys regularly
- Use strong MongoDB passwords
- Enable 2FA on Telegram account
- Review admin logs regularly

## Support

For issues, check:
1. `logs/errors.log` for error details
2. Terminal output for initialization messages
3. MongoDB connection with: `mongosh` or MongoDB Compass
4. Telegram Bot API status: https://status.telegram.org/

## Resources

- Pyrogram Docs: https://docs.pyrogram.org/
- Telegram Bot API: https://core.telegram.org/bots/api
- yt-dlp: https://github.com/yt-dlp/yt-dlp
- MongoDB: https://docs.mongodb.com/
- PyTgCalls: https://github.com/pytgcalls/pytgcalls

---

**Last Updated:** January 2025
