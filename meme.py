import os
import random
import requests
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_trending_news():
    """Get trending news from Google News (RSS) without API key"""
    try:
        url = "https://news.google.com/rss"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')[:5]  # Get top 5 news items
        
        trending_news = []
        for item in items:
            title = item.title.text
            # Remove the source from title (e.g., " - BBC News")
            title = title.split(' - ')[0]
            trending_news.append(title)
        
        return trending_news
    
    except Exception as e:
        logger.error(f"Error fetching trending news: {e}")
        return ["Bitcoin hits all-time high", "Elon Musk tweets about crypto", "NFT sales surge", "Web3 adoption growing", "Metaverse expansion continues"]

def generate_meme_coin_name(news_headline):
    """Generate a meme coin name based on news headline"""
    try:
        # Common crypto suffixes
        suffixes = ['Coin', 'Token', 'Inu', 'Fi', 'Swap', 'Moon', 'Rocket', 'Floki', 'Doge', 'Shib', 'Pump', 'Labs', 'DAO', 'Farm']
        
        # Process the headline
        words = news_headline.split()
        if len(words) > 3:
            # Take first 2-3 meaningful words
            words = [w for w in words if len(w) > 3][:3]
        
        # Combine with suffix
        base_name = ''.join([w.capitalize() for w in words])
        suffix = random.choice(suffixes)
        
        # 50% chance to add a number
        if random.random() > 0.5:
            number = random.choice(['69', '420', '777', '1000', '2024', '999'])
            return f"{base_name}{suffix}{number}"
        
        return f"{base_name}{suffix}"
    
    except Exception as e:
        logger.error(f"Error generating meme coin name: {e}")
        return "SuperDogeInu420"

def send_to_telegram(message):
    """Send message to Telegram channel"""
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            logger.error("Telegram credentials not set")
            return False
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    
    except Exception as e:
        logger.error(f"Error sending to Telegram: {e}")
        return False

def main():
    try:
        logger.info("Starting meme coin name generator...")
        
        # Get trending news
        news_items = get_trending_news()
        logger.info(f"Found {len(news_items)} trending news items")
        
        # Generate meme coin names
        meme_coins = []
        for news in news_items:
            coin_name = generate_meme_coin_name(news)
            meme_coins.append((news, coin_name))
        
        # Prepare Telegram message
        message = "<b>🔥 Trending Meme Coin Ideas 🔥</b>\n\n"
        message += "Based on today's trending news:\n\n"
        
        for news, coin in meme_coins:
            message += f"📰 <i>{news}</i>\n"
            message += f"💰 <b>{coin}</b>\n\n"
        
        message += "Generated at: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Send to Telegram
        if send_to_telegram(message):
            logger.info("Message sent to Telegram successfully")
        else:
            logger.error("Failed to send message to Telegram")
    
    except Exception as e:
        logger.error(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()
