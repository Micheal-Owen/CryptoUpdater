# Worldcoin Price Tracker Telegram Bot 🌍💰

A feature-rich Telegram bot that tracks Worldcoin cryptocurrency prices, provides real-time alerts, and offers detailed price analytics.

## Features 🚀

### Price Monitoring
- Real-time price tracking using CoinGecko API
- 24-hour price history tracking
- Price trend analysis
- Statistical data (24h high/low/average)

### Alerts System
- Automatic $1 increase notifications
- Custom price target alerts
- Multiple alert thresholds per user
- Alert status tracking

### Commands
- `/start` - Welcome message and command list
- `/track` - Start tracking Worldcoin price
- `/stop` - Stop price tracking
- `/price` - Get current price
- `/setalert <price>` - Set custom price alert
- `/alerts` - List your active alerts
- `/trend` - Get price trend analysis
- `/stats` - Get price statistics
- `/settings` - Manage notification preferences

## Installation 🔧

1. Clone the repository:
```bash
git clone <your-repository-url>
cd WORLDCOIN_UPDATER
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your Telegram Bot Token from BotFather
```bash
cp .env.example .env
```

4. Edit `.env` file:
```env
BOT_TOKEN=your_bot_token_here
```

## Usage 🎯

1. Start the bot:
```bash
python telegram_WC_Bot.py
```

2. Open Telegram and search for your bot
3. Start interacting with the bot using the available commands

## Project Structure 📁

```
WORLDCOIN_UPDATER/
├── telegram_WC_Bot.py     # Main bot implementation
├── .env                   # Environment variables (private)
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation
```

## Security 🔒

- Sensitive data (bot tokens, API keys) are stored in `.env` file
- `.env` file is excluded from version control
- Proper error handling and logging implemented
- Secure environment variable management

## Error Handling 🛠️

The bot includes comprehensive error handling:
- Connection error recovery
- API failure handling
- Invalid user input management
- Logging system for debugging

## Deployment 🚀

1. Set up your hosting environment
2. Install required dependencies
3. Create and configure `.env` file
4. Run the bot using a process manager (e.g., PM2)

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Future Enhancements 🔮

- [ ] Price alerts based on percentage changes
- [ ] Multiple cryptocurrency support
- [ ] Custom notification intervals
- [ ] Technical analysis indicators
- [ ] User preference persistence
- [ ] Group chat support

## Dependencies 📦

- python-telegram-bot
- requests
- python-dotenv
- threading
- logging

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that is short and to the point. It lets people do anything they want with your code as long as they provide attribution back to you and don't hold you liable. The main points of the MIT license are:

- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ✅ Sublicense

The only requirement is that the license and copyright notice must be included in all copies or substantial portions of the software.

## Support 💬

For support, please open an issue in the repository or contact Owen Kakembo.

## Acknowledgments 🙏

- CoinGecko API for price data
- Telegram Bot API

---
Created with ❤️ by Owen Kakembo

© 2024 Owen Kakembo. All Rights Reserved.
