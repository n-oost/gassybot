#!/usr/bin/env python3
"""
Discord Gas Price Bot

A Discord bot that fetches and posts local gas prices at regular intervals.
"""

import asyncio
import logging
import os
import random
import sys
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    """Set up logging configuration for both file and console output."""
    log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handler
    file_handler = logging.FileHandler('bot.log')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=[file_handler, console_handler]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

class GasPriceBot(commands.Bot):
    """Discord bot for fetching and posting gas prices."""
    
    def __init__(self):
        """Initialize the bot with necessary configurations."""
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!gas',
            intents=intents,
            help_command=None
        )
        
        # Configuration from environment variables
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID', 0))
        self.target_area = os.getenv('TARGET_AREA', '10001')
        self.api_key = os.getenv('GAS_PRICE_API_KEY')
        self.update_interval = int(os.getenv('UPDATE_INTERVAL_HOURS', 6))
        
        # Validate required configuration
        if not self.token:
            logger.error("DISCORD_BOT_TOKEN environment variable is required")
            sys.exit(1)
        
        if not self.channel_id:
            logger.error("DISCORD_CHANNEL_ID environment variable is required")
            sys.exit(1)
        
        # HTTP session for API requests
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"Bot initialized for area: {self.target_area}")
        logger.info(f"Update interval: {self.update_interval} hours")
    
    async def setup_hook(self):
        """Called when the bot is starting up."""
        self.session = aiohttp.ClientSession()
        logger.info("Bot setup completed")
    
    async def close(self):
        """Clean up resources when the bot shuts down."""
        if self.session:
            await self.session.close()
        await super().close()
        logger.info("Bot closed successfully")
    
    async def on_ready(self):
        """Called when the bot has successfully connected to Discord."""
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        
        # Start the gas price posting task
        if not self.post_gas_prices.is_running():
            self.post_gas_prices.start()
            logger.info("Gas price posting task started")
    
    async def on_error(self, event, *args, **kwargs):
        """Handle bot errors."""
        logger.error(f"Bot error in event {event}: {args}, {kwargs}", exc_info=True)
    
    async def fetch_gas_prices(self) -> Dict[str, float]:
        """
        Fetch gas prices for the configured area.
        
        Currently uses mock data. Replace with real API implementation if available.
        
        Returns:
            Dictionary with gas types and their prices
        """
        try:
            # Mock implementation - replace with real API call
            await asyncio.sleep(0.1)  # Simulate API call delay
            
            # Generate realistic gas price data
            base_prices = {
                'Regular': 3.45,
                'Mid-Grade': 3.75,
                'Premium': 4.05,
                'Diesel': 3.85
            }
            
            # Add some random variation (±$0.30)
            prices = {}
            for gas_type, base_price in base_prices.items():
                variation = random.uniform(-0.30, 0.30)
                prices[gas_type] = round(base_price + variation, 2)
            
            logger.info(f"Fetched gas prices for {self.target_area}: {prices}")
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching gas prices: {e}")
            return {}
    
    def format_gas_prices_message(self, prices: Dict[str, float]) -> str:
        """
        Format gas prices into a Discord message.
        
        Args:
            prices: Dictionary of gas types and prices
            
        Returns:
            Formatted message string
        """
        if not prices:
            return "❌ Unable to fetch gas prices at this time. Please try again later."
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message_lines = [
            "⛽ **Current Gas Prices** ⛽",
            f"📍 Location: {self.target_area}",
            f"🕒 Updated: {timestamp}",
            "",
            "💰 **Prices per gallon:**"
        ]
        
        # Sort prices by value for better display
        sorted_prices = sorted(prices.items(), key=lambda x: x[1])
        
        for gas_type, price in sorted_prices:
            emoji = self.get_gas_type_emoji(gas_type)
            message_lines.append(f"{emoji} {gas_type}: **${price:.2f}**")
        
        message_lines.extend([
            "",
            "🔄 Next update in approximately 6 hours",
            "💡 Use `!gas now` for instant price check"
        ])
        
        return "\n".join(message_lines)
    
    def get_gas_type_emoji(self, gas_type: str) -> str:
        """Get emoji for gas type."""
        emoji_map = {
            'Regular': '🟢',
            'Mid-Grade': '🟡',
            'Premium': '🔴',
            'Diesel': '🔵'
        }
        return emoji_map.get(gas_type, '⛽')
    
    @tasks.loop(hours=6)  # Default to 6 hours, will be updated in start method
    async def post_gas_prices(self):
        """Periodically post gas prices to the designated channel."""
        try:
            channel = self.get_channel(self.channel_id)
            if not channel:
                logger.error(f"Could not find channel with ID: {self.channel_id}")
                return
            
            prices = await self.fetch_gas_prices()
            message = self.format_gas_prices_message(prices)
            
            await channel.send(message)
            logger.info(f"Gas prices posted to channel {channel.name}")
            
        except Exception as e:
            logger.error(f"Error posting gas prices: {e}")
    
    @post_gas_prices.before_loop
    async def before_post_gas_prices(self):
        """Wait until the bot is ready before starting the loop."""
        await self.wait_until_ready()
        # Update the loop interval from configuration
        self.post_gas_prices.change_interval(hours=self.update_interval)
        logger.info(f"Gas price posting interval set to {self.update_interval} hours")
    
    @commands.command(name='now')
    async def get_current_prices(self, ctx):
        """Command to get current gas prices immediately."""
        try:
            logger.info(f"Manual gas price request from {ctx.author}")
            
            # Send a "typing" indicator while fetching prices
            async with ctx.typing():
                prices = await self.fetch_gas_prices()
                message = self.format_gas_prices_message(prices)
            
            await ctx.send(message)
            
        except Exception as e:
            logger.error(f"Error in manual price request: {e}")
            await ctx.send("❌ Sorry, I couldn't fetch gas prices right now. Please try again later.")
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information."""
        help_text = """
🤖 **Gas Price Bot Help**

**Commands:**
• `!gas now` - Get current gas prices immediately
• `!gas help` - Show this help message

**Features:**
• Automatic gas price updates every 6 hours
• Real-time price checking on demand
• Covers multiple gas types (Regular, Mid-Grade, Premium, Diesel)

**Location:** Currently tracking prices for {area}

For support or issues, contact your server administrator.
        """.format(area=self.target_area)
        
        await ctx.send(help_text)
    
    async def run_bot(self):
        """Run the bot with proper error handling."""
        try:
            logger.info("Starting Discord bot...")
            await self.start(self.token)
        except discord.LoginFailure:
            logger.error("Failed to login to Discord. Check your bot token.")
        except Exception as e:
            logger.error(f"Bot encountered an error: {e}")
        finally:
            await self.close()

async def main():
    """Main entry point for the bot."""
    bot = GasPriceBot()
    
    try:
        await bot.run_bot()
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())