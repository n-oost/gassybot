#!/usr/bin/env python3
"""
GassyBot - Discord Gas Price Bot

A highly efficient Discord bot that fetches and posts local gas prices
at regular intervals with minimal resource usage and high reliability.
"""

import asyncio
import logging
import os
import random
from datetime import datetime, timezone
from typing import Optional, Dict, List

import discord
from discord.ext import commands, tasks
import aiohttp


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gassybot.log') if os.path.exists('.') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)


class GasPriceService:
    """Service for fetching gas prices with mock data fallback."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            connector=aiohttp.TCPConnector(limit=10, limit_per_host=5)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_gas_prices(self, area: str) -> Dict[str, float]:
        """
        Fetch gas prices for the specified area.
        
        Currently uses mock data since most gas price APIs require paid subscriptions.
        In production, replace this with actual API calls to services like:
        - GasBuddy API (requires enterprise access)
        - AAA Gas Prices API
        - Local government fuel price APIs
        """
        try:
            logger.info(f"Fetching gas prices for area: {area}")
            
            # Mock realistic gas prices with some variation
            base_prices = {
                "Regular": 3.45,
                "Mid-Grade": 3.75,
                "Premium": 4.05,
                "Diesel": 3.89
            }
            
            # Add some realistic variation (±$0.20)
            prices = {}
            for fuel_type, base_price in base_prices.items():
                variation = random.uniform(-0.20, 0.20)
                prices[fuel_type] = round(base_price + variation, 2)
            
            # Simulate API delay
            await asyncio.sleep(0.5)
            
            logger.info(f"Successfully fetched prices for {area}")
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching gas prices: {e}")
            # Return fallback prices in case of error
            return {
                "Regular": 3.50,
                "Mid-Grade": 3.80,
                "Premium": 4.10,
                "Diesel": 3.95
            }


class GassyBot(commands.Bot):
    """Main Discord bot class for gas price updates."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!gas ',
            intents=intents,
            help_command=commands.DefaultHelpCommand(no_category='Commands')
        )
        
        self.gas_service = None
        self.target_channel_id = int(os.getenv('DISCORD_CHANNEL_ID', '0'))
        self.area = os.getenv('GAS_AREA', 'Default City, State')
        self.update_interval_hours = int(os.getenv('UPDATE_INTERVAL_HOURS', '6'))
        
    async def setup_hook(self):
        """Initialize bot resources."""
        logger.info("Setting up GassyBot...")
        self.gas_service = GasPriceService()
        
        # Start the price update task
        if not self.price_updater.is_running():
            self.price_updater.start()
            logger.info(f"Started price updater with {self.update_interval_hours}h interval")
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        logger.info(f'Monitoring area: {self.area}')
        
        if self.target_channel_id:
            channel = self.get_channel(self.target_channel_id)
            if channel:
                logger.info(f'Target channel: #{channel.name}')
            else:
                logger.warning(f'Could not find channel with ID {self.target_channel_id}')
    
    async def on_command_error(self, ctx, error):
        """Global error handler."""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        logger.error(f"Command error in {ctx.command}: {error}")
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ I don't have permission to do that.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I need additional permissions to run this command.")
        else:
            await ctx.send("❌ An error occurred while processing the command.")
    
    @tasks.loop(hours=6)  # Default 6 hours, will be updated based on env var
    async def price_updater(self):
        """Automatically post gas price updates."""
        try:
            if not self.target_channel_id:
                logger.warning("No target channel configured for automatic updates")
                return
                
            channel = self.get_channel(self.target_channel_id)
            if not channel:
                logger.error(f"Could not find target channel {self.target_channel_id}")
                return
            
            async with self.gas_service as service:
                prices = await service.fetch_gas_prices(self.area)
                embed = self.create_price_embed(prices, self.area, auto_update=True)
                await channel.send(embed=embed)
                logger.info(f"Posted automatic price update to #{channel.name}")
                
        except Exception as e:
            logger.error(f"Error in price updater: {e}")
    
    @price_updater.before_loop
    async def before_price_updater(self):
        """Wait for bot to be ready before starting the loop."""
        await self.wait_until_ready()
        # Update the loop interval based on environment variable
        self.price_updater.change_interval(hours=self.update_interval_hours)
    
    def create_price_embed(self, prices: Dict[str, float], area: str, auto_update: bool = False) -> discord.Embed:
        """Create a formatted embed for gas prices."""
        title = "⛽ Current Gas Prices"
        if auto_update:
            title += " (Auto Update)"
            
        embed = discord.Embed(
            title=title,
            description=f"📍 **{area}**",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Add price fields
        for fuel_type, price in prices.items():
            emoji = {
                "Regular": "🟢",
                "Mid-Grade": "🟡", 
                "Premium": "🔴",
                "Diesel": "🟤"
            }.get(fuel_type, "⛽")
            
            embed.add_field(
                name=f"{emoji} {fuel_type}",
                value=f"**${price:.2f}**/gal",
                inline=True
            )
        
        embed.set_footer(text="Prices are estimates and may vary by station")
        return embed
    
    @commands.command(name='prices', help='Get current gas prices for the configured area')
    async def get_prices(self, ctx):
        """Manual command to get current gas prices."""
        async with ctx.typing():
            try:
                async with self.gas_service as service:
                    prices = await service.fetch_gas_prices(self.area)
                    embed = self.create_price_embed(prices, self.area)
                    await ctx.send(embed=embed)
                    logger.info(f"Manual price request by {ctx.author} in #{ctx.channel}")
                    
            except Exception as e:
                logger.error(f"Error getting prices: {e}")
                await ctx.send("❌ Sorry, I couldn't fetch the gas prices right now. Please try again later.")
    
    @commands.command(name='area', help='Get the currently configured area')
    async def get_area(self, ctx):
        """Show the currently configured area."""
        embed = discord.Embed(
            title="📍 Configured Area",
            description=f"Currently monitoring: **{self.area}**",
            color=0x0099ff
        )
        embed.add_field(
            name="Update Interval", 
            value=f"Every {self.update_interval_hours} hours", 
            inline=False
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='status', help='Get bot status and next update time')
    async def get_status(self, ctx):
        """Show bot status information."""
        embed = discord.Embed(
            title="🤖 GassyBot Status",
            color=0x0099ff,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Bot uptime info
        embed.add_field(name="Status", value="🟢 Online", inline=True)
        embed.add_field(name="Guilds", value=str(len(self.guilds)), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.latency * 1000)}ms", inline=True)
        
        # Update info
        if self.price_updater.is_running():
            next_run = self.price_updater.next_iteration
            if next_run:
                next_run_str = f"<t:{int(next_run.timestamp())}:R>"
            else:
                next_run_str = "Soon"
            embed.add_field(name="Next Auto Update", value=next_run_str, inline=False)
        else:
            embed.add_field(name="Auto Updates", value="❌ Disabled", inline=False)
        
        embed.add_field(name="Monitoring Area", value=self.area, inline=False)
        
        await ctx.send(embed=embed)


async def main():
    """Main function to run the bot."""
    # Validate required environment variables
    discord_token = os.getenv('DISCORD_TOKEN')
    if not discord_token:
        logger.error("DISCORD_TOKEN environment variable is required!")
        return
    
    # Create and run bot
    bot = GassyBot()
    
    try:
        logger.info("Starting GassyBot...")
        await bot.start(discord_token)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()
        logger.info("GassyBot shut down complete")


if __name__ == "__main__":
    asyncio.run(main())