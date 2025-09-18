# GassyBot ⛽

A highly efficient Discord bot that fetches and posts local gas prices at regular intervals. Built with Python using async programming best practices for minimal resource usage and high reliability.

## Features

- 🔄 **Automatic Updates**: Posts gas prices every 6 hours (configurable)
- 📍 **Location-Based**: Configure specific area monitoring via environment variables
- ⚡ **Highly Efficient**: Async programming with minimal resource footprint
- 🛡️ **Reliable**: Comprehensive error handling and logging
- 🚀 **Easy Deployment**: Ready for deployment on Render with one-click setup
- 💬 **Discord Commands**: Manual price checking and bot status commands

## Commands

- `!gas prices` - Get current gas prices for the configured area
- `!gas area` - Show the currently configured monitoring area
- `!gas status` - Display bot status and next update time
- `!gas help` - Show all available commands

## Quick Setup

### 1. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "GassyBot")
3. Go to "Bot" section and click "Add Bot"
4. Copy the bot token (you'll need this for deployment)
5. Under "Privileged Gateway Intents", enable:
   - Message Content Intent (required for commands)

### 2. Invite Bot to Server

1. In Developer Portal, go to "OAuth2" > "URL Generator"
2. Select scopes: `bot`
3. Select bot permissions: `Send Messages`, `Use Slash Commands`, `Read Message History`
4. Use generated URL to invite bot to your server

### 3. Get Channel ID

1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
2. Right-click the channel where you want price updates
3. Click "Copy ID" - this is your `DISCORD_CHANNEL_ID`

## Local Development

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/n-oost/gassybot.git
cd gassybot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Edit `.env` with your configuration:
```env
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=123456789012345678
GAS_AREA=Your City, State
UPDATE_INTERVAL_HOURS=6
```

5. Run the bot:
```bash
python bot.py
```

## Deployment on Render

### Method 1: One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Method 2: Manual Deploy

1. **Fork this repository** to your GitHub account

2. **Create new Web Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" > "Web Service"
   - Connect your GitHub account and select the forked repository

3. **Configure Service**:
   - **Name**: `gassybot` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: `Free` (sufficient for most use cases)

4. **Set Environment Variables**:
   Click "Advanced" and add these environment variables:
   ```
   DISCORD_TOKEN = your_discord_bot_token_here
   DISCORD_CHANNEL_ID = your_channel_id_here
   GAS_AREA = Your City, State
   UPDATE_INTERVAL_HOURS = 6
   ```

5. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your bot
   - Check logs for any issues

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DISCORD_TOKEN` | ✅ | Your Discord bot token | `MTIz...` |
| `DISCORD_CHANNEL_ID` | ✅ | Channel ID for automatic updates | `123456789012345678` |
| `GAS_AREA` | ❌ | Area to monitor (default: "Default City, State") | `"New York, NY"` |
| `UPDATE_INTERVAL_HOURS` | ❌ | Hours between updates (default: 6) | `6` |

## Gas Price Data

Currently, the bot uses mock data that simulates realistic gas prices with variation. This is because most gas price APIs (like GasBuddy) require paid enterprise subscriptions.

### Integrating Real Data

To integrate with real gas price APIs, modify the `fetch_gas_prices` method in `bot.py`:

```python
async def fetch_gas_prices(self, area: str) -> Dict[str, float]:
    # Replace mock data with actual API calls
    # Examples:
    # - GasBuddy Enterprise API
    # - AAA Gas Price API
    # - Local government fuel price APIs
    pass
```

## Architecture

- **Async Design**: Built with `asyncio` and `discord.py` for efficient resource usage
- **Error Handling**: Comprehensive logging and graceful error recovery
- **Mock Data**: Realistic gas price simulation for demonstration
- **Configurable**: All settings via environment variables
- **Production Ready**: Structured for reliable deployment

## Monitoring and Logs

### Local Logs
- Console output for real-time monitoring
- `gassybot.log` file for persistent logging

### Render Logs
- Access logs via Render dashboard
- Real-time log streaming available
- Automatic log rotation

## Troubleshooting

### Common Issues

1. **Bot doesn't respond to commands**:
   - Ensure Message Content Intent is enabled in Discord Developer Portal
   - Check bot has necessary permissions in the server

2. **Bot not posting automatic updates**:
   - Verify `DISCORD_CHANNEL_ID` is correct
   - Check bot has Send Messages permission in the target channel

3. **Deployment fails on Render**:
   - Check all required environment variables are set
   - Review build logs for missing dependencies

### Support

For issues or questions:
1. Check the logs for error messages
2. Verify all environment variables are correctly set
3. Ensure Discord bot permissions are properly configured

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.