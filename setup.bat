# VTH MUSIC Bot Setup Script

@echo off
REM VTH MUSIC Bot - Automated Setup Script for Windows
REM This script helps setup the bot with minimal manual steps

echo.
echo ========================================
echo VTH MUSIC Bot - Setup Assistant
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Python found: 
python --version

REM Create virtual environment
echo.
echo [2/5] Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo.
echo [4/5] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Try running manually: pip install -r requirements.txt
    pause
    exit /b 1
)
echo Dependencies installed successfully.

REM Check for .env file
echo.
echo [5/5] Checking configuration...
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo.
    echo Please follow these steps:
    echo 1. Copy: .env.example to .env
    echo 2. Edit .env with your credentials:
    echo    - BOT_TOKEN from @BotFather
    echo    - API_ID and API_HASH from my.telegram.org
    echo    - OWNER_ID (your Telegram user ID)
    echo    - MONGO_URI (MongoDB connection)
    echo    - STRING_SESSION (from pyrogram)
    echo.
    echo 3. To generate STRING_SESSION:
    echo    python -m pyrogram create_session
    echo.
    echo 4. Then run: python run.py
    echo.
) else (
    echo .env file found.
    echo.
    echo ========================================
    echo Setup Complete!
    echo ========================================
    echo.
    echo To start the bot, run:
    echo   python run.py
    echo.
)

REM Offer to show documentation
echo.
set /p show_docs="View QUICKSTART.md? (y/n): "
if /i "%show_docs%"=="y" (
    start notepad QUICKSTART.md
)

echo.
echo Setup script complete.
pause
