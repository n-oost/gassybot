#!/usr/bin/env python3
"""
Health check script for GassyBot deployment monitoring.
This can be used by monitoring services to check if the bot is running properly.
"""

import asyncio
import sys
import os
import signal
from datetime import datetime

# Simple health check that validates environment and basic functionality
def health_check():
    """Perform basic health checks."""
    checks = []
    
    # Check required environment variables
    discord_token = os.getenv('DISCORD_TOKEN')
    if discord_token:
        checks.append("✅ DISCORD_TOKEN configured")
    else:
        checks.append("❌ DISCORD_TOKEN missing")
        
    channel_id = os.getenv('DISCORD_CHANNEL_ID')
    if channel_id and channel_id.isdigit():
        checks.append("✅ DISCORD_CHANNEL_ID configured")
    else:
        checks.append("⚠️  DISCORD_CHANNEL_ID not configured (auto-updates disabled)")
    
    # Check Python version
    if sys.version_info >= (3, 8):
        checks.append(f"✅ Python {sys.version.split()[0]} (compatible)")
    else:
        checks.append(f"❌ Python {sys.version.split()[0]} (requires 3.8+)")
    
    # Check if bot file exists and is readable
    if os.path.exists('bot.py') and os.access('bot.py', os.R_OK):
        checks.append("✅ bot.py accessible")
    else:
        checks.append("❌ bot.py not found or not readable")
    
    # Check requirements
    if os.path.exists('requirements.txt'):
        checks.append("✅ requirements.txt found")
    else:
        checks.append("❌ requirements.txt missing")
    
    return checks

def main():
    """Run health check and return appropriate exit code."""
    print(f"🏥 GassyBot Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    checks = health_check()
    
    for check in checks:
        print(check)
    
    # Count failures
    failures = sum(1 for check in checks if check.startswith("❌"))
    warnings = sum(1 for check in checks if check.startswith("⚠️"))
    
    print("=" * 50)
    
    if failures > 0:
        print(f"❌ Health check FAILED ({failures} errors, {warnings} warnings)")
        return 1
    elif warnings > 0:
        print(f"⚠️  Health check PASSED with warnings ({warnings} warnings)")
        return 0
    else:
        print("✅ Health check PASSED (all systems go)")
        return 0

if __name__ == "__main__":
    exit(main())