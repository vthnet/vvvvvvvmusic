# VTH MUSIC Bot - Quick Start Guide

**5-Minute Quick Start** for running the bot locally.

## Prerequisites
- Python 3.10+
- MongoDB (local or cloud)
- Telegram account (for API credentials)

## Step 1: Get Credentials (5 mins)

### Telegram Bot Token
1. Message `@BotFather` on Telegram
2. Send `/newbot`
3. Follow wizard, get token

### Telegram API Credentials
1. Go to https://my.telegram.org/
2. Login and go to "API Development tools"
3. Copy `API_ID` and `API_HASH`

### Your User ID
- Message `@userinfobot` to get your ID

## Step 2: Setup Project (2 mins)

```bash
# Clone/extract project
cd VTHMusic_New_Bot_API10_3

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Bot (3 mins)

### Copy template
```bash
copy .env.example .env
# or: cp .env.example .env  (macOS/Linux)
```

### Edit `.env` file
```
BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz
API_ID=12345678
API_HASH=abcdefghijklmnopqrstuvwxyz123456
OWNER_ID=987654321
MONGO_URI=mongodb://localhost:27017
STRING_SESSION=BQA-...
```

### Generate Pyrogram Session
```bash
python -m pyrogram create_session
# Follow prompts:
# - API ID: <from my.telegram.org>
# - API Hash: <from my.telegram.org>
# - Phone: <your phone with country code>
# - Code: <Telegram verification code>
```

Copy the generated session string to `.env` as `STRING_SESSION`.

## Step 4: Start Bot (1 min)

```bash
python run.py
```

You should see:
```
🎵 VTH MUSIC BOT STARTING...
✅ VTH MUSIC BOT STARTED SUCCESSFULLY
Bot is running and listening for commands...
```

## Step 5: Test Commands

Open Telegram and:

1. **Private Chat**: `/start`
2. **Play Music**: `/play never gonna give you up`
3. **Show Queue**: `/queue`
4. **Pause**: `/pause`
5. **Skip**: `/skip`
6. **Stop**: `/stop`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `BOT_TOKEN is required` | Check .env file, run `python -m pyrogram create_session` |
| `MongoDB connection failed` | Start MongoDB: `net start MongoDB` (Windows) or verify MONGO_URI |
| Bot doesn't respond | Check logs in `logs/bot.log` for errors |
| Can't join voice chat | Regenerate STRING_SESSION with correct credentials |

## File Structure

```
app/
├── bot.py              ← Main bot logic
├── config.py           ← Settings
├── database/           ← MongoDB operations
├── services/           ← YouTube, lyrics, downloads
├── utils/              ← Logging, permissions, helpers
├── ui/                 ← Messages and buttons
└── player/             ← Player state management

logs/                   ← Auto-created log files
requirements.txt        ← Python dependencies
.env                    ← Your configuration (create from .env.example)
README.md               ← Full documentation
SETUP.md                ← Detailed setup guide
```

## Logs Location

Bot creates 4 log files in `logs/` directory:
- `bot.log` - Bot activity
- `playback.log` - Music events
- `errors.log` - Errors
- `admin.log` - Admin actions

## Next Steps

After successful start:
1. Add bot to a group
2. Make bot group admin
3. Try `/play` command
4. Use player buttons
5. Check `logs/bot.log` for info

## Commands Available

| Command | Usage |
|---------|-------|
| `/start` | Show home |
| `/help` | Show help |
| `/play` | Play song |
| `/queue` | Show queue |
| `/pause` | Pause |
| `/resume` | Resume |
| `/skip` | Next song |
| `/stop` | Stop playing |

## Player Buttons

| Button | Action |
|--------|--------|
| ⏮ | Previous |
| ⏸/▶ | Pause/Resume |
| ⏭ | Next |
| 🔁 | Loop mode |
| ⚡ | Autoplay |
| 🔀 | Shuffle |
| ❤️ | Favorite |
| ☰ | Queue |
| ↺ | Replay |
| ⬇️ | Download |
| ✕ | Close |

## Features

✅ YouTube music playback
✅ Queue management
✅ Loop modes (OFF/ONE/ALL)
✅ Shuffle & autoplay
✅ Favorites with MongoDB
✅ Play history
✅ DJ mode for groups
✅ Volume control
✅ Professional logging

## Support

1. Check `logs/errors.log` for error details
2. Read SETUP.md for detailed setup
3. Read VERIFICATION.md for testing
4. Check bot.log for debug info

## Common Issues

### "No module named 'pyrogram'"
```bash
pip install pyrogram tgcrypto
```

### MongoDB connection error
```bash
# Windows
net start MongoDB

# Linux
sudo systemctl start mongodb

# Or use MongoDB Atlas
# Update MONGO_URI in .env
```

### Bot not responding
- Check .env has correct BOT_TOKEN
- Check logs/bot.log
- Verify bot is running: See "Bot is running..." message

## SSH/Remote Deployment

```bash
# Copy project to server
scp -r . user@server:/path/to/bot

# On server:
ssh user@server
cd /path/to/bot
python -m venv .env
source .venv/bin/activate
pip install -r requirements.txt
# Configure .env
nohup python run.py > bot.log 2>&1 &
```

---

**Ready to run!** Questions? Check SETUP.md or VERIFICATION.md for details.
