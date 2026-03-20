#!/usr/bin/env python3
"""
Fam Tree Bot Pro - Run Script
=============================
Main entry point for the bot

Usage:
    python run.py

Requirements:
    - Python 3.8+
    - All dependencies from requirements.txt
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.main import FamTreeBot

def check_token():
    """Check if bot token is set"""
    from config.config import BOT_TOKEN
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("=" * 60)
        print("❌ ERROR: Bot token not configured!")
        print("=" * 60)
        print("\nPlease follow these steps:")
        print("1. Create a .env file in the project root")
        print("2. Add your bot token:")
        print("   BOT_TOKEN=your_bot_token_here")
        print("\nGet your bot token from @BotFather on Telegram")
        print("=" * 60)
        return False
    return True

async def main():
    """Main function"""
    
    if not check_token():
        sys.exit(1)
    
    print("=" * 60)
    print("🌲 💘 Fam Tree Bot Pro")
    print("=" * 60)
    print("\n📦 Features:")
    print("   🌳 Family Tree System")
    print("   🌐 Friend Circle")
    print("   🏡 Garden & Farming")
    print("   💰 Rob, Kill & Insurance")
    print("   🎮 Mini Games")
    print("   🏭 Factory System")
    print("   📊 Leaderboards")
    print("   🔧 25+ Utility Commands")
    print("\n" + "=" * 60)
    
    bot = FamTreeBot()
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user!")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
