#!/usr/bin/env python3
"""
VTH MUSIC Bot - Configuration Validator

This script validates your .env file and provides setup instructions.
Run this before running the bot to ensure all credentials are properly configured.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if not env_path.exists():
        print(f"{Colors.RED}✗ .env file not found!{Colors.END}")
        print(f"\nCreate it by running:")
        print(f"  {Colors.YELLOW}copy .env.example .env{Colors.END}  (Windows)")
        print(f"  {Colors.YELLOW}cp .env.example .env{Colors.END}  (macOS/Linux)")
        return False
    print(f"{Colors.GREEN}✓ .env file found{Colors.END}")
    return True

def validate_credentials():
    """Validate all required credentials."""
    load_dotenv()
    
    issues = []
    warnings = []
    
    # Check BOT_TOKEN
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token or bot_token.startswith("PUT_"):
        issues.append("BOT_TOKEN - Get from @BotFather on Telegram")
    elif ":" not in bot_token or len(bot_token) < 20:
        issues.append("BOT_TOKEN - Invalid format (should be numbers:letters)")
    else:
        print(f"{Colors.GREEN}✓ BOT_TOKEN configured{Colors.END}")
    
    # Check API_ID
    api_id = os.getenv("API_ID", "").strip()
    if not api_id or api_id.startswith("PUT_"):
        issues.append("API_ID - Get from my.telegram.org")
    elif not api_id.isdigit() or len(api_id) < 4:
        issues.append("API_ID - Must be a number (get from my.telegram.org)")
    else:
        print(f"{Colors.GREEN}✓ API_ID configured{Colors.END}")
    
    # Check API_HASH
    api_hash = os.getenv("API_HASH", "").strip()
    if not api_hash or api_hash.startswith("PUT_"):
        issues.append("API_HASH - Get from my.telegram.org")
    elif len(api_hash) < 20:
        issues.append("API_HASH - Invalid (should be long alphanumeric string)")
    else:
        print(f"{Colors.GREEN}✓ API_HASH configured{Colors.END}")
    
    # Check OWNER_ID
    owner_id = os.getenv("OWNER_ID", "").strip()
    if not owner_id or owner_id.startswith("PUT_"):
        issues.append("OWNER_ID - Your Telegram user ID (ask @userinfobot)")
    elif not owner_id.isdigit() or len(owner_id) < 8:
        issues.append("OWNER_ID - Must be numeric (ask @userinfobot)")
    else:
        print(f"{Colors.GREEN}✓ OWNER_ID configured{Colors.END}")
    
    # Check STRING_SESSION
    string_session = os.getenv("STRING_SESSION", "").strip()
    if not string_session or string_session.startswith("PUT_"):
        issues.append("STRING_SESSION - Generate with: python -m pyrogram create_session")
    elif not string_session.startswith(("BQA", "BQD")):
        warnings.append("STRING_SESSION - Doesn't look like a valid session (should start with BQA or BQD)")
    else:
        print(f"{Colors.GREEN}✓ STRING_SESSION configured{Colors.END}")
    
    # Check MONGO_URI (optional, has default)
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    if "mongodb" in mongo_uri.lower():
        print(f"{Colors.GREEN}✓ MONGO_URI configured{Colors.END}")
    else:
        warnings.append("MONGO_URI - Doesn't look like MongoDB URI")
    
    return issues, warnings

def print_setup_instructions():
    """Print step-by-step setup instructions."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}VTH MUSIC BOT - CONFIGURATION SETUP GUIDE{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    print(f"{Colors.YELLOW}Step 1: Get Bot Token{Colors.END}")
    print("  1. Message @BotFather on Telegram")
    print("  2. Send: /newbot")
    print("  3. Follow the wizard")
    print("  4. Copy the token and paste in .env as BOT_TOKEN\n")
    
    print(f"{Colors.YELLOW}Step 2: Get API Credentials{Colors.END}")
    print("  1. Go to https://my.telegram.org/")
    print("  2. Login with your Telegram account")
    print("  3. Click 'API Development tools'")
    print("  4. Copy API_ID (numeric) and API_HASH (string) to .env\n")
    
    print(f"{Colors.YELLOW}Step 3: Get Your User ID{Colors.END}")
    print("  1. Message @userinfobot on Telegram")
    print("  2. Send any message to get your ID")
    print("  3. Copy the ID and paste in .env as OWNER_ID\n")
    
    print(f"{Colors.YELLOW}Step 4: Generate Pyrogram Session{Colors.END}")
    print("  1. Activate virtual environment")
    print("  2. Run: python -m pyrogram create_session")
    print("  3. Enter API_ID and API_HASH from above")
    print("  4. Enter your phone number with country code")
    print("  5. Enter the verification code from Telegram")
    print("  6. Copy the generated session string to .env as STRING_SESSION\n")
    
    print(f"{Colors.YELLOW}Step 5: Configure MongoDB (Optional){Colors.END}")
    print("  - Default: mongodb://localhost:27017")
    print("  - Or use MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/")
    print("  - Update MONGO_URI in .env if using different connection\n")

def main():
    """Main validation function."""
    print(f"\n{Colors.BLUE}VTH MUSIC BOT - Configuration Validator{Colors.END}\n")
    
    # Check .env file exists
    if not check_env_file():
        print_setup_instructions()
        sys.exit(1)
    
    # Validate credentials
    issues, warnings = validate_credentials()
    
    if issues:
        print(f"\n{Colors.RED}❌ Missing or Invalid Configuration:{Colors.END}")
        for issue in issues:
            print(f"  {Colors.RED}✗{Colors.END} {issue}")
        print_setup_instructions()
        sys.exit(1)
    
    if warnings:
        print(f"\n{Colors.YELLOW}⚠️  Warnings:{Colors.END}")
        for warning in warnings:
            print(f"  {Colors.YELLOW}!{Colors.END} {warning}")
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}✓ All required credentials are configured!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"\nYou can now run the bot:")
    print(f"  {Colors.YELLOW}python run.py{Colors.END}\n")

if __name__ == "__main__":
    main()
