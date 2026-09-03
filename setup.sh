#!/bin/bash
# VTH MUSIC Bot Setup Script for Linux/macOS
# Automated setup with minimal manual steps

echo ""
echo "========================================"
echo "VTH MUSIC Bot - Setup Assistant"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.10+"
    echo "macOS: brew install python3"
    echo "Linux: sudo apt-get install python3"
    exit 1
fi

echo "[1/5] Python found:"
python3 --version

# Create virtual environment
echo ""
echo "[2/5] Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo ""
echo "[3/5] Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo ""
echo "[4/5] Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Try running manually: pip install -r requirements.txt"
    exit 1
fi
echo "Dependencies installed successfully."

# Check for .env file
echo ""
echo "[5/5] Checking configuration..."
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: .env file not found!"
    echo ""
    echo "Please follow these steps:"
    echo "1. Copy configuration template:"
    echo "   cp .env.example .env"
    echo ""
    echo "2. Edit .env with your credentials:"
    echo "   nano .env"
    echo ""
    echo "   Required fields:"
    echo "   - BOT_TOKEN from @BotFather"
    echo "   - API_ID and API_HASH from my.telegram.org"
    echo "   - OWNER_ID (your Telegram user ID)"
    echo "   - MONGO_URI (MongoDB connection)"
    echo "   - STRING_SESSION (from pyrogram)"
    echo ""
    echo "3. To generate STRING_SESSION:"
    echo "   python -m pyrogram create_session"
    echo ""
    echo "4. Then run: python run.py"
    echo ""
else
    echo ".env file found."
    echo ""
    echo "========================================"
    echo "Setup Complete!"
    echo "========================================"
    echo ""
    echo "To start the bot, run:"
    echo "  python run.py"
    echo ""
    echo "For help, see:"
    echo "  - QUICKSTART.md (quick start)"
    echo "  - SETUP.md (detailed setup)"
    echo "  - README.md (full documentation)"
    echo ""
fi
