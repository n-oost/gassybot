#!/usr/bin/env python3
"""
Configuration validation script for GassyBot.
Run this script to verify your environment is properly configured.
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and provide guidance."""
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    
    if not env_path.exists():
        if env_example_path.exists():
            print("⚠️  .env file not found. Please copy .env.example to .env and configure it:")
            print("   cp .env.example .env")
            return False
        else:
            print("❌ Neither .env nor .env.example found!")
            return False
    
    print("✅ .env file found")
    return True

def check_required_vars():
    """Check if required environment variables are set."""
    required_vars = {
        'DISCORD_BOT_TOKEN': 'Your Discord bot token',
        'DISCORD_CHANNEL_ID': 'The Discord channel ID for gas price updates'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value == f'your_{var.lower()}_here' or 'your_' in value:
            missing_vars.append(f"  {var}: {description}")
            print(f"❌ {var} is not properly configured")
        else:
            print(f"✅ {var} is configured")
    
    if missing_vars:
        print("\n⚠️  Please configure the following variables in your .env file:")
        for var in missing_vars:
            print(var)
        return False
    
    return True

def check_optional_vars():
    """Check optional environment variables and show current values."""
    optional_vars = {
        'TARGET_AREA': '10001',
        'UPDATE_INTERVAL_HOURS': '6',
        'LOG_LEVEL': 'INFO'
    }
    
    print("\n📋 Optional configuration (current values):")
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        print(f"   {var}: {value}")

def main():
    """Main configuration check."""
    print("🔧 GassyBot Configuration Checker\n")
    
    # Load .env if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ python-dotenv is available")
    except ImportError:
        print("⚠️  python-dotenv not installed. Install dependencies with: pip install -r requirements.txt")
        print("   Checking system environment variables instead...\n")
    
    all_good = True
    
    # Check .env file
    if not check_env_file():
        all_good = False
    
    print()
    
    # Check required variables
    if not check_required_vars():
        all_good = False
    
    # Show optional variables
    check_optional_vars()
    
    print("\n" + "="*50)
    
    if all_good:
        print("🎉 Configuration looks good! You can start the bot with: python bot.py")
    else:
        print("❌ Configuration issues found. Please fix them before running the bot.")
        print("\n📖 For setup instructions, see: README.md")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)