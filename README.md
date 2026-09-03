# VTH MUSIC — Premium Telegram Music Bot

A professional, high-performance Telegram music bot built with Pyrogram, PyTgCalls, yt-dlp, and MongoDB.

## ✨ Features

### Core Music Playback
- 🎵 YouTube audio playback with high-quality streaming
- 📝 Play by song name or YouTube URL
- 🔎 Intelligent search and results
- ▶️ Play/Pause/Skip/Previous controls
- 📋 Real queue management system

### Advanced Features
- 🔁 Loop modes: OFF / ONE / ALL
- 🔀 Real shuffle (respects currently playing track)
- ⚡ Autoplay - automatically adds similar songs
- ❤️ User favorites system with MongoDB persistence
- 📜 Play history tracking
- 🎤 Lyrics fetching (extensible service)
- 📥 Audio/video downloads (yt-dlp + FFmpeg)
- 🔊 Volume control per group
- 🎛 DJ mode for group control
- ⚙️ Group-specific settings
- 👥 User and group management

### Premium Features
- 🎨 Custom emoji support (Telegram Bot API 10.3)
- 🎬 Random snap video player cards
- 📊 Statistics and analytics
- 👑 Owner admin panel
- 📢 Broadcast system
- 🚨 Professional logging system
- 🔒 Centralized permission system

## 🚀 Setup

### Prerequisites
- Python 3.10+
- MongoDB (local or cloud)
- Telegram Bot API credentials (from BotFather)
- Telegram API credentials (from my.telegram.org)
- Pyrogram user session (for voice chat access)

### Installation

1. **Clone or extract the project:**
   ```bash
   cd VTHMusic_New_Bot_API10_3
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Fill in your credentials:
     ```
     BOT_TOKEN=your_bot_token_from_botfather
     API_ID=your_api_id_from_my_telegram_org
     API_HASH=your_api_hash_from_my_telegram_org
     MONGO_URI=mongodb://localhost:27017  # Or your MongoDB connection string
     OWNER_ID=your_telegram_user_id
     STRING_SESSION=your_pyrogram_session_string
     ```

5. **Generate Pyrogram session:**
   ```bash
   python -m pyrogram create_session
   ```
   Follow the prompts to authenticate and save the session string.

6. **Run the bot:**
   ```bash
   python run.py
   ```

## 📚 Architecture

### Database Layer (`app/database/`)
- `client.py` - MongoDB connection management
- `models.py` - Pydantic data models
- `users.py` - User operations
- `groups.py` - Group and settings operations
- `favorites.py` - Favorites management
- `history.py` - Play history
- `dj.py` - DJ user management
- `statistics.py` - Statistics tracking

### Services (`app/services/`)
- `search.py` - YouTube search and metadata extraction
- `lyrics.py` - Lyrics service (extensible)
- `downloader.py` - Audio/video download management

### Player (`app/player/`)
- `state.py` - Player state management per chat

### UI (`app/ui/`)
- `buttons.py` - Premium inline keyboard generation
- `messages.py` - Message templates and formatting

### Utilities (`app/utils/`)
- `logger.py` - Professional logging system
- `permissions.py` - Permission checking system
- `helpers.py` - Helper functions
- `errors.py` - Custom exceptions
- `emoji.py` - Centralized emoji registry

### Handlers (`app/handlers/`)
- `start.py` - Home screen and utilities
- `player.py` - Player state (legacy, being phased out)

## 🎮 Commands

### User Commands
- `/start` - Show home screen
- `/play <song>` - Play a song
- `/queue` - View current queue
- `/pause` - Pause playback
- `/resume` - Resume playback
- `/skip` - Skip current track
- `/stop` - Stop playback

### Player Controls (Buttons)
- ⏮ Previous
- ⏸/▶ Pause/Resume
- ⏭ Next
- 🔁 Loop (OFF → ONE → ALL)
- ⚡ Autoplay
- 🔀 Shuffle
- ❤️ Favorite
- ☰ Queue
- ↺ Replay
- ⬇️ Download
- ❌ Close Player

## 🔧 Configuration

### Environment Variables
See `.env.example` for all available options.

### Custom Emojis
Edit `app/config.py` to update custom emoji IDs for your Telegram premium account.

### Logging
Logs are stored in `logs/` directory:
- `bot.log` - General bot logs
- `playback.log` - Playback events
- `errors.log` - Errors and exceptions
- `admin.log` - Admin actions

## 📊 Database Schema

### Collections
- `users` - User profiles and stats
- `groups` - Group information
- `favorites` - User favorite tracks
- `history` - Play history
- `settings` - Group settings
- `djs` - DJ assignments
- `statistics` - Bot statistics snapshots

## 🤝 Contributing

Contributions are welcome! Please ensure:
1. No placeholder code or TODO comments
2. Proper error handling
3. Database operations are async
4. Logging is used appropriately

## 📄 License

This project is provided as-is for educational and personal use.

## 🔗 Links

- Created By: [@valriks](https://t.me/valriks)
- Privacy: https://t.me/valriks
- Policy: https://t.me/valriks
- Support: https://t.me/valriks

---

**VTH MUSIC** — Premium music, clean controls, and a faster player built for Telegram.

*Fast • Stable • Premium*
