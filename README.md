# GassyBot 🤖⛽

A highly efficient Discord bot that fetches and posts current local gas prices at regular intervals. Built with Python using asynchronous programming best practices for optimal performance and reliability.

## Features

- 🔄 **Automatic Updates**: Posts gas prices every 6 hours (configurable)
- ⚡ **On-Demand Prices**: Get instant gas price updates with `!gas now`
- 🌍 **Location-Based**: Configurable target area (zip code, city, etc.)
- 📊 **Multiple Gas Types**: Regular, Mid-Grade, Premium, and Diesel prices
- 🛡️ **Robust Error Handling**: Comprehensive logging and error recovery
- 🚀 **Production Ready**: Optimized for deployment on Render
- 🔒 **Secure**: Environment variable configuration for sensitive data

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Discord bot token ([Create a Discord Application](https://discord.com/developers/applications))
- Discord server with a channel for gas price updates

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/n-oost/gassybot.git
   cd gassybot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in your configuration:
   ```env
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   DISCORD_CHANNEL_ID=123456789012345678
   TARGET_AREA=10001
   UPDATE_INTERVAL_HOURS=6
   LOG_LEVEL=INFO
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

### Getting Your Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Copy the token and add it to your `.env` file
6. Under "Privileged Gateway Intents", enable "Message Content Intent"

### Getting Your Discord Channel ID

1. Enable Developer Mode in Discord (User Settings → App Settings → Advanced → Developer Mode)
2. Right-click on the channel where you want gas prices posted
3. Click "Copy Channel ID"
4. Add this ID to your `.env` file

### Inviting the Bot to Your Server

1. In the Discord Developer Portal, go to the "OAuth2" → "URL Generator" section
2. Select the following scopes:
   - `bot`
   - `applications.commands`
3. Select the following bot permissions:
   - `Send Messages`
   - `Use Slash Commands`
   - `Read Message History`
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | ✅ | - | Your Discord bot token |
| `DISCORD_CHANNEL_ID` | ✅ | - | ID of the channel for gas price updates |
| `TARGET_AREA` | ❌ | `10001` | Target area (zip code, city name, etc.) |
| `UPDATE_INTERVAL_HOURS` | ❌ | `6` | Hours between automatic updates |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `GAS_PRICE_API_KEY` | ❌ | - | API key for gas price service (if using real API) |

### Commands

- `!gas now` - Get current gas prices immediately
- `!gas help` - Show help information and available commands

## Deployment on Render

### Step 1: Prepare Your Repository

1. Ensure all files are committed to your Git repository
2. Push your code to GitHub, GitLab, or Bitbucket

### Step 2: Create a Render Service

1. Go to [Render](https://render.com) and sign up/login
2. Click "New +" and select "Web Service"
3. Connect your repository
4. Configure the service:
   - **Name**: `gassybot` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`

### Step 3: Configure Environment Variables

In the Render dashboard, add the following environment variables:

```
DISCORD_BOT_TOKEN=your_actual_bot_token
DISCORD_CHANNEL_ID=your_actual_channel_id
TARGET_AREA=your_target_area
UPDATE_INTERVAL_HOURS=6
LOG_LEVEL=INFO
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your bot
3. Monitor the logs to ensure successful deployment

## API Integration

### Current Implementation

The bot currently uses mock data to generate realistic gas prices. This ensures the bot works out of the box without requiring additional API keys.

### Adding Real Gas Price API

To integrate with a real gas price API:

1. **Find a suitable API** (e.g., GasBuddy API, AAA Gas Prices API)
2. **Update the `fetch_gas_prices` method** in `bot.py`
3. **Add API configuration** to your environment variables
4. **Handle API rate limits** and error responses

Example implementation structure:
```python
async def fetch_gas_prices(self) -> Dict[str, float]:
    """Fetch real gas prices from API."""
    try:
        url = f"https://api.example.com/gas-prices"
        params = {
            'location': self.target_area,
            'api_key': self.api_key
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self.parse_api_response(data)
            else:
                logger.error(f"API request failed: {response.status}")
                return {}
    except Exception as e:
        logger.error(f"Error fetching gas prices: {e}")
        return {}
```

## Logging

The bot logs to both the console and a `bot.log` file:

- **Console**: Real-time logging for development and monitoring
- **File**: Persistent logs for debugging and audit trails

Log levels available: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## Performance Optimization

### Resource Usage

- **Memory**: Minimal memory footprint with efficient data structures
- **CPU**: Asynchronous operations prevent blocking
- **Network**: HTTP session reuse and connection pooling
- **Storage**: Rotating log files to prevent disk space issues

### Reliability Features

- **Automatic Reconnection**: Discord.py handles connection drops
- **Error Recovery**: Graceful handling of API failures
- **Rate Limit Handling**: Built-in Discord API rate limiting
- **Graceful Shutdown**: Proper cleanup of resources

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check bot token validity
   - Verify bot permissions in Discord server
   - Check console/log for error messages

2. **Channel not found**
   - Verify channel ID is correct
   - Ensure bot has access to the channel

3. **Gas prices not updating**
   - Check log for scheduled task errors
   - Verify internet connectivity
   - Check API rate limits (if using real API)

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your environment variables.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues, questions, or contributions:

1. Check the [Issues](https://github.com/n-oost/gassybot/issues) section
2. Create a new issue with detailed information
3. Include log files and error messages for bug reports

---

**Happy gas price tracking! ⛽🤖**