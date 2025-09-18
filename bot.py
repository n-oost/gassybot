import os
import asyncio
import logging
import random
from datetime import datetime

import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables from a .env file
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# Default to 0 if not set, which will prevent the bot from starting the loop
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", 0))
TARGET_AREA = os.getenv("TARGET_AREA", "your_default_area")
# How often to post prices, in hours
FETCH_INTERVAL_HOURS = 6

# --- Logging Setup ---
# Set up logging to both a file and the console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# --- Bot Setup ---
# Define the bot's intents. Message Content is required for commands.
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Mock Gas Price API ---
async def fetch_gas_prices(area: str):
    """
    Placeholder function to mock fetching gas prices.
    In a real-world scenario, you would replace this with an HTTP request
    to a gas price API.
    """
    logging.info(f"Fetching mock gas prices for area: {area}")
    await asyncio.sleep(1)  # Simulate network latency of a real API call

    # Generate realistic-looking random data
    mock_prices = [
        {"name": "Speedy Gas", "price": f"${random.uniform(3.50, 4.50):.2f}"},
        {"name": "Local Fuel Stop", "price": f"${random.uniform(3.50, 4.50):.2f}"},
        {"name": "Highway Fuel Co.", "price": f"${random.uniform(3.50, 4.50):.2f}"},
    ]
    # Return prices sorted from cheapest to most expensive
    return sorted(mock_prices, key=lambda x: x['price'])

# --- Core Bot Logic ---
@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    logging.info(f'Logged in as {bot.user.name} ({bot.user.id})')
    logging.info('Starting gas price update loop...')
    post_gas_prices.start()

@tasks.loop(hours=FETCH_INTERVAL_HOURS)
async def post_gas_prices():
    """Main task to fetch and post gas prices at regular intervals."""
    if TARGET_CHANNEL_ID == 0:
        logging.warning("TARGET_CHANNEL_ID is not set. The automated price post will not run.")
        return

    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        logging.error(f"Could not find channel with ID {TARGET_CHANNEL_ID}. Please check the ID.")
        return

    try:
        prices = await fetch_gas_prices(TARGET_AREA)
        if not prices:
            logging.info("No gas prices were found to post.")
            return

        embed = discord.Embed(
            title=f"⛽ Gas Prices in {TARGET_AREA}",
            description="Here are the latest regular unleaded gas prices.",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )

        for station in prices:
            embed.add_field(name=station['name'], value=station['price'], inline=False)
        
        embed.set_footer(text="Data is for informational purposes only.")

        await channel.send(embed=embed)
        logging.info(f"Successfully posted gas prices to channel #{channel.name}")

    except Exception as e:
        logging.error(f"An error occurred in the post_gas_prices loop: {e}", exc_info=True)
        try:
            await channel.send("Sorry, I couldn't fetch the gas prices right now due to an error.")
        except discord.Forbidden:
            logging.error(f"Missing permissions to send messages in channel #{channel.name}.")


@post_gas_prices.before_loop
async def before_post_gas_prices():
    """Ensures the bot is fully connected before the task loop starts."""
    await bot.wait_until_ready()


# --- Manual Command ---
@bot.command(name="gas")
async def manual_gas_check(ctx):
    """Manually triggers a gas price check in the current channel."""
    logging.info(f"Manual gas price check triggered by {ctx.author.name} in #{ctx.channel.name}")
    await ctx.send(f"Fetching gas prices for {TARGET_AREA}...")
    
    try:
        prices = await fetch_gas_prices(TARGET_AREA)
        if not prices:
            await ctx.send("Could not retrieve gas prices at this time.")
            return

        embed = discord.Embed(
            title=f"⛽ Gas Prices in {TARGET_AREA}",
            description="Here are the latest regular unleaded gas prices.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )

        for station in prices:
            embed.add_field(name=station['name'], value=station['price'], inline=False)
            
        embed.set_footer(text="Data is for informational purposes only.")

        await ctx.send(embed=embed)
    except Exception as e:
        logging.error(f"An error occurred during manual gas check: {e}", exc_info=True)
        await ctx.send("Sorry, there was an error fetching the gas prices.")

# --- Main Execution ---
if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        logging.error("FATAL: DISCORD_BOT_TOKEN environment variable is not set. The bot cannot start.")
    else:
        bot.run(DISCORD_BOT_TOKEN)