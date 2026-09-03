# VTH MUSIC Bot - Startup Guide

## 🚀 First Time Setup

### Step 1: Validate Configuration

Run the configuration validator to see what's missing:

```bash
python validate_config.py
```

This will tell you exactly which credentials you need to configure.

### Step 2: Get Your Telegram Credentials

Follow the validator's output or these instructions:

#### Bot Token (from BotFather)
1. Open Telegram and search for **`@BotFather`**
2. Send `/newbot`
3. Follow the wizard to create a new bot
4. Copy the token (format: `123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz`)
5. Paste into `.env` as `BOT_TOKEN=...`

#### API Credentials (from my.telegram.org)
1. Go to **https://my.telegram.org/**
2. Login with your Telegram account
3. Click **"API Development tools"**
4. Copy `API_ID` (numeric value like 12345678)
5. Copy `API_HASH` (long alphanumeric string)
6. Paste both into `.env`:
   ```
   API_ID=12345678
   API_HASH=abcdefghijklmnopqrstuvwxyz...
   ```

#### Your User ID (OWNER_ID)
1. Open Telegram and search for **`@userinfobot`**
2. Send any message
3. It will reply with your user ID
4. Paste into `.env` as `OWNER_ID=...`

#### Pyrogram Session (STRING_SESSION)
This requires the API credentials from above first:

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Generate session
python -m pyrogram create_session

# Follow the prompts:
# - App API ID: (paste your API_ID)
# - App API hash: (paste your API_HASH)
# - Phone number: +1234567890 (with country code)
# - Code: (Telegram will send a code, enter it)
# - Password: (if you have 2FA enabled)

# It will generate a session string starting with BQA...
# Copy the entire string to .env as STRING_SESSION=...
```

### Step 3: Edit .env File

Open `.env` and fill in all the values:

```bash
# Edit the file
notepad .env  # Windows
# nano .env  # Linux/macOS
```

**Example .env file** (with fake values for illustration):
```
BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTuvwxyzABCDEFGH
API_ID=12345678
API_HASH=abcdefg1234567890xyz123456789abcd
OWNER_ID=987654321
MONGO_URI=mongodb://localhost:27017
STRING_SESSION=BQAsomeverylong...sessionstringhere...xyz
GENIUS_API_KEY=
```

### YouTube Authentication

If yt-dlp reports `Sign in to confirm you're not a bot`, configure fresh YouTube
browser cookies. Export them in Netscape format, Base64-encode the file, and set
the result as `YOUTUBE_COOKIES_B64` in the deployment environment. Do not commit
the cookie file or put its contents in the Dockerfile.

For a local cookie file, set `YOUTUBE_COOKIES` to its mounted path instead.

### Step 4: Verify Configuration

Run the validator again to confirm everything is correct:

```bash
python validate_config.py
```

Expected output:
```
✓ BOT_TOKEN configured
✓ API_ID configured
✓ API_HASH configured
✓ OWNER_ID configured
✓ STRING_SESSION configured
✓ MONGO_URI configured

============================================================
✓ All required credentials are configured!
============================================================

You can now run the bot:
  python run.py
```

### Step 5: Start the Bot

Once all credentials are validated:

```bash
python run.py
```

Expected startup output:
```
🎵 VTH MUSIC BOT STARTING...
✅ VTH MUSIC BOT STARTED SUCCESSFULLY
Bot is running and listening for commands...
```

If you see this, the bot is running! 🎉

---

## ⚙️ Configuration Options

### Required Credentials
- **BOT_TOKEN** - From BotFather (required for bot to work)
- **API_ID** - From my.telegram.org (required for voice chat)
- **API_HASH** - From my.telegram.org (required for voice chat)
- **OWNER_ID** - Your Telegram user ID (required for admin features)
- **STRING_SESSION** - From pyrogram (required for voice chat)

### Optional Credentials
- **MONGO_URI** - MongoDB connection (default: `mongodb://localhost:27017`)
- **GENIUS_API_KEY** - For lyrics integration (optional)

---

## 🗄️ MongoDB Setup

### Option A: Local MongoDB (Default)

**Windows:**
1. Download from https://www.mongodb.com/try/download/community
2. Install with default settings
3. MongoDB starts automatically as Windows service
4. Connection string: `mongodb://localhost:27017`

**Linux:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

**macOS:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

### Option B: MongoDB Atlas (Cloud - Recommended)

1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create a cluster
4. Create database user with password
5. Whitelist your IP address (or allow from anywhere)
6. Copy connection string: `mongodb+srv://user:password@cluster.mongodb.net/`
7. Paste into `.env` as `MONGO_URI=...`

---

## ❌ Common Issues & Solutions

### Error: "BOT_TOKEN not configured"
**Solution:** You didn't set BOT_TOKEN in .env file
- Run: `python validate_config.py` to see what's missing
- Get token from @BotFather
- Edit .env and add it

### Error: "Permission denied: '.venv\\Scripts\\python.exe'"
**Solution:** Windows antivirus or permissions issue
- Try: Running PowerShell as Administrator
- Or: Temporarily disable antivirus
- Or: Use system Python instead of venv

### Error: "ModuleNotFoundError: No module named 'pytgcalls'"
**Solution:** Dependencies not installed
```bash
pip install -r requirements.txt
```

### Error: "MongoDB connection failed"
**Solution:** MongoDB not running
- Windows: Check if MongoDB service is running
- Linux: `sudo systemctl start mongodb`
- macOS: `brew services start mongodb-community`
- Or use MongoDB Atlas instead (cloud version)

### Bot starts but doesn't respond to commands
**Solution:** Check the following:
1. Bot is added to groups with admin rights
2. BOT_TOKEN is correct (check logs/bot.log)
3. API_ID and API_HASH are correct
4. STRING_SESSION is valid (regenerate if needed)
5. Check `logs/errors.log` for detailed error messages

### Can't generate Pyrogram session
**Solution:** Make sure:
1. API_ID and API_HASH are correct
2. You're using your personal Telegram account (not bot)
3. You have 2FA disabled or know your password
4. Your phone number includes country code: +1234567890

---

## 📋 Checklist Before Running

- [ ] `.env` file exists (not `.env.example`)
- [ ] BOT_TOKEN filled in (from BotFather)
- [ ] API_ID filled in (numeric, from my.telegram.org)
- [ ] API_HASH filled in (long string, from my.telegram.org)
- [ ] OWNER_ID filled in (your Telegram user ID)
- [ ] STRING_SESSION filled in (from pyrogram)
- [ ] MongoDB running or MongoDB Atlas configured
- [ ] Run `python validate_config.py` - all green ✓
- [ ] Virtual environment activated
- [ ] Requirements installed: `pip install -r requirements.txt`

---

## 🚀 Ready to Run?

Once all checklist items are done:

```bash
python run.py
```

Watch for the success message:
```
✅ VTH MUSIC BOT STARTED SUCCESSFULLY
Bot is running and listening for commands...
```

Then open Telegram and:
1. Send `/start` to your bot
2. Try `/play your favorite song`
3. Use the player buttons to control playback

---

## 📖 Additional Resources

- **Full Documentation:** See README.md
- **Setup Guide:** See SETUP.md
- **Testing Checklist:** See VERIFICATION.md
- **Bot Architecture:** See IMPLEMENTATION_SUMMARY.md

---

## 💬 Getting Help

If you're stuck:

1. Check the error message in terminal
2. Check logs: `logs/errors.log`
3. Run: `python validate_config.py` to see what's misconfigured
4. Review SETUP.md for detailed troubleshooting
5. Check that your credentials are correct (copy-paste from official sources)

---

**That's it! Your bot should now be running.** 🎵

Enjoy premium music on Telegram! 🎉
