import requests
from telebot import TeleBot
import time
import threading
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class WorldcoinTelegramBot:
    def __init__(self, bot_token):
        """
        Initialize Worldcoin Telegram Bot with improved error handling
        
        :param bot_token: Telegram Bot Token from BotFather
        """
        # Configure bot with custom exceptions and connection parameters
        self.bot = TeleBot(
            token=bot_token, 
            parse_mode=None,
            threaded=True,
            num_threads=2,
            skip_pending=True
        )
        
        self.tracking_users = {}  # Store users and their tracking preferences
        self.price_check_interval = 60  # Check price every minute
        self.bot_token = bot_token
        self.price_history = []  # Store recent price history for trends
        
    def get_worldcoin_price(self):
        """
        Fetch current Worldcoin price from CoinGecko with improved error handling
        
        :return: Current price of Worldcoin in USD or None if failed
        """
        try:
            url = 'https://api.coingecko.com/api/v3/simple/price?ids=world-coin&vs_currencies=usd'
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise exception for bad responses
            data = response.json()
            if 'world-coin' in data and 'usd' in data['world-coin']:
                return data['world-coin']['usd']
            logger.error("Unexpected API response format")
            return None
        except requests.RequestException as e:
            logger.error(f"Price fetch error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching price: {e}")
            return None
    
    def get_price_trend(self):
        """
        Calculate price trend based on recent history
        """
        if len(self.price_history) < 2:
            return "Insufficient data for trend analysis"
            
        last_price = self.price_history[-1]
        prev_price = self.price_history[0]
        change = ((last_price - prev_price) / prev_price) * 100
        
        if change > 5:
            return f"📈 Strong Upward Trend (+{change:.2f}%)"
        elif change > 0:
            return f"↗️ Slight Upward Trend (+{change:.2f}%)"
        elif change < -5:
            return f"📉 Strong Downward Trend ({change:.2f}%)"
        elif change < 0:
            return f"↘️ Slight Downward Trend ({change:.2f}%)"
        else:
            return "➡️ Stable Price"
            
    def set_price_alert(self, user_id, target_price):
        """
        Set custom price alert for user
        """
        if user_id not in self.tracking_users:
            self.tracking_users[user_id] = {
                'tracking': True,
                'last_notification_price': int(self.get_worldcoin_price()),
                'alerts': []
            }
        
        self.tracking_users[user_id]['alerts'].append({
            'target': float(target_price),
            'triggered': False
        })
        
    def check_price_alerts(self, user_id, current_price):
        """
        Check if any price alerts should be triggered
        """
        if user_id not in self.tracking_users:
            return []
            
        messages = []
        user_data = self.tracking_users[user_id]
        
        for alert in user_data['alerts']:
            if not alert['triggered']:
                if current_price >= alert['target']:
                    messages.append(
                        f"🎯 Price Alert: Worldcoin has reached ${current_price}\n"
                        f"Your target price was: ${alert['target']}"
                    )
                    alert['triggered'] = True
                    
        return messages
        
    def get_price_stats(self):
        """
        Calculate price statistics
        """
        if not self.price_history:
            return "No price data available"
            
        current = self.price_history[-1]
        high = max(self.price_history)
        low = min(self.price_history)
        avg = sum(self.price_history) / len(self.price_history)
        
        return (
            f"📊 Worldcoin Price Statistics:\n"
            f"Current: ${current:.2f}\n"
            f"24h High: ${high:.2f}\n"
            f"24h Low: ${low:.2f}\n"
            f"24h Average: ${avg:.2f}"
        )
    
    def start_price_tracking(self, user_id, initial_price=None):
        """
        Start tracking price for a specific user with additional checks
        
        :param user_id: Telegram user ID
        :param initial_price: Initial price to start tracking from
        """
        try:
            if user_id not in self.tracking_users:
                current_price = self.get_worldcoin_price()
                if current_price is None:
                    logger.error("Failed to start price tracking: Could not fetch initial price")
                    return False
                
                self.tracking_users[user_id] = {
                    'last_notification_price': initial_price or int(current_price),
                    'tracking': True,
                    'alerts': []
                }
                logger.info(f"Started price tracking for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error in start_price_tracking for user {user_id}: {e}")
            return False
    
    def stop_price_tracking(self, user_id):
        """
        Stop tracking price for a specific user
        
        :param user_id: Telegram user ID
        """
        if user_id in self.tracking_users:
            self.tracking_users[user_id]['tracking'] = False
            del self.tracking_users[user_id]
            return True
        return False
    
    def continuous_price_check(self):
        """
        Continuously check Worldcoin price with robust error handling
        """
        while True:
            try:
                current_price = self.get_worldcoin_price()
                
                if current_price is not None:
                    # Update price history
                    self.price_history.append(float(current_price))
                    if len(self.price_history) > 24:  # Keep last 24 hours
                        self.price_history.pop(0)
                    
                    # Check alerts for each user
                    for user_id, user_data in list(self.tracking_users.items()):
                        if user_data['tracking']:
                            # Check regular price increase
                            if int(current_price) > user_data['last_notification_price']:
                                try:
                                    message = (
                                        f"🚨 Worldcoin Price Alert 🚨\n\n"
                                        f"Current Price: ${current_price}\n"
                                        f"Price has increased by $1 since last check!"
                                    )
                                    self.bot.send_message(user_id, message)
                                    user_data['last_notification_price'] = int(current_price)
                                except Exception as send_error:
                                    logger.error(f"Message send error to {user_id}: {send_error}")
                            
                            # Check custom price alerts
                            alert_messages = self.check_price_alerts(user_id, current_price)
                            for msg in alert_messages:
                                try:
                                    self.bot.send_message(user_id, msg)
                                except Exception as send_error:
                                    logger.error(f"Alert message send error to {user_id}: {send_error}")
                
                time.sleep(self.price_check_interval)
            
            except Exception as e:
                logger.error(f"Continuous check error: {e}")
                time.sleep(self.price_check_interval)
    
    def setup_bot_handlers(self):
        """
        Set up Telegram bot command handlers with improved error logging
        """
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            try:
                welcome_text = (
                    "Welcome to the Worldcoin Price Tracker Bot! 🚀\n\n"
                    "Available commands:\n"
                    "/start - Show this welcome message\n"
                    "/track - Start tracking Worldcoin price\n"
                    "/stop - Stop tracking Worldcoin price\n"
                    "/price - Get current Worldcoin price\n"
                    "/setalert <price> - Set custom price alert\n"
                    "/alerts - List your active alerts\n"
                    "/trend - Get price trend analysis\n"
                    "/stats - Get price statistics\n"
                    "/settings - Manage notification preferences"
                )
                self.bot.reply_to(message, welcome_text)
            except Exception as e:
                logger.error(f"Welcome message error: {e}")
        
        @self.bot.message_handler(commands=['track'])
        def start_tracking(message):
            try:
                user_id = message.from_user.id
                if self.start_price_tracking(user_id):
                    self.bot.reply_to(message, "Price tracking started! You'll receive notifications when Worldcoin price increases by $1.")
                else:
                    current_price = self.get_worldcoin_price()
                    if current_price is None:
                        self.bot.reply_to(message, "Sorry, I couldn't start tracking prices right now. Please try again later.")
                    else:
                        self.bot.reply_to(message, "You are already tracking Worldcoin prices.")
            except Exception as e:
                logger.error(f"Track command error: {e}")
                self.bot.reply_to(message, "An error occurred while starting price tracking. Please try again later.")
        
        @self.bot.message_handler(commands=['stop'])
        def stop_tracking(message):
            user_id = message.from_user.id
            if self.stop_price_tracking(user_id):
                self.bot.reply_to(message, "Price tracking stopped.")
            else:
                self.bot.reply_to(message, "You are not currently tracking prices.")
        
        @self.bot.message_handler(commands=['price'])
        def current_price(message):
            price = self.get_worldcoin_price()
            if price:
                self.bot.reply_to(message, f"Current Worldcoin Price: ${price}")
            else:
                self.bot.reply_to(message, "Unable to fetch current price.")
        
        @self.bot.message_handler(commands=['setalert'])
        def set_alert(message):
            try:
                args = message.text.split()
                if len(args) != 2:
                    self.bot.reply_to(message, "Usage: /setalert <price>\nExample: /setalert 10.50")
                    return
                
                try:
                    target_price = float(args[1])
                    if target_price <= 0:
                        self.bot.reply_to(message, "Please enter a positive price value")
                        return
                        
                    self.set_price_alert(message.from_user.id, target_price)
                    self.bot.reply_to(
                        message,
                        f"✅ Alert set! You'll be notified when Worldcoin reaches ${target_price}"
                    )
                except ValueError:
                    self.bot.reply_to(message, "Invalid price value. Please enter a number.")
            except Exception as e:
                logger.error(f"Set alert error: {e}")
                
        @self.bot.message_handler(commands=['alerts'])
        def list_alerts(message):
            try:
                user_id = message.from_user.id
                if user_id not in self.tracking_users or not self.tracking_users[user_id]['alerts']:
                    self.bot.reply_to(message, "You have no active price alerts")
                    return
                    
                alerts_text = "Your Active Price Alerts:\n\n"
                for idx, alert in enumerate(self.tracking_users[user_id]['alerts'], 1):
                    status = "✅ Triggered" if alert['triggered'] else "⏳ Waiting"
                    alerts_text += f"{idx}. ${alert['target']} - {status}\n"
                    
                self.bot.reply_to(message, alerts_text)
            except Exception as e:
                logger.error(f"List alerts error: {e}")
                
        @self.bot.message_handler(commands=['trend'])
        def show_trend(message):
            try:
                trend = self.get_price_trend()
                self.bot.reply_to(message, f"Worldcoin Price Trend:\n{trend}")
            except Exception as e:
                logger.error(f"Show trend error: {e}")
                
        @self.bot.message_handler(commands=['stats'])
        def show_stats(message):
            try:
                stats = self.get_price_stats()
                self.bot.reply_to(message, stats)
            except Exception as e:
                logger.error(f"Show stats error: {e}")
    
    def run(self):
        """
        Start the Telegram bot and price tracking
        """
        try:
            # Remove webhook to avoid conflicts
            self.bot.remove_webhook()
            
            # Setup bot command handlers
            self.setup_bot_handlers()
            
            # Start continuous price checking in a separate thread
            price_thread = threading.Thread(target=self.continuous_price_check)
            price_thread.daemon = True
            price_thread.start()
            
            # Start bot polling with error handling
            print("Bot is running. Press Ctrl+C to stop.")
            self.bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise

def main():
    # Get bot token from environment variable
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        logger.error("No BOT_TOKEN found in environment variables!")
        print("Error: Please make sure you have set up the BOT_TOKEN in your .env file")
        return
    
    try:
        # Initialize and run the bot
        bot = WorldcoinTelegramBot(BOT_TOKEN)
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == '__main__':
    main()