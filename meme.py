import os
import random
import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meme_coins.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Telegram configuration with validation
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def validate_telegram_credentials():
    """Verify Telegram credentials are properly set"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("MISSING TELEGRAM CREDENTIALS!")
        logger.info(f"BOT_TOKEN: {'SET' if TELEGRAM_BOT_TOKEN else 'NOT SET'}")
        logger.info(f"CHAT_ID: {'SET' if TELEGRAM_CHAT_ID else 'NOT SET'}")
        return False
    return True

class TrendScraper:
    @staticmethod
    def get_google_trends():
        """Scrape trending search terms with better error handling"""
        try:
            url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml-xml')
            return [item.title.text for item in soup.find_all('item')[:5]]
        except Exception as e:
            logger.error(f"Google Trends failed: {str(e)}")
            return ["Bitcoin ETF", "AI Crypto", "Meme Coin", "Web3 Games", "NFT Art"]

    # ... (keep other scraping methods unchanged) ...

class MemeCoinGenerator:
    # ... (keep existing generator logic) ...

def send_telegram_report(assets):
    """Enhanced Telegram sender with delivery verification"""
    if not validate_telegram_credentials():
        return False

    message = "🔥 *VIRAL MEME COIN ALERTS* 🔥\n\n"
    for trend, name, ticker in assets:
        message += (
            f"📈 Trend: `{trend}`\n"
            f"🪙 Coin: `{name}`\n"
            f"📊 Ticker: `{ticker}`\n"
            f"🚀 Pair: `{ticker}/USDT`\n\n"
        )
    message += f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_"

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'MarkdownV2',
                'disable_web_page_preview': True
            },
            timeout=10
        )
        
        # Detailed response analysis
        if response.status_code == 200:
            logger.info(f"Telegram message sent successfully! Message ID: {response.json()['result']['message_id']}")
            return True
        else:
            logger.error(f"Telegram API Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Telegram connection failed: {str(e)}")
        return False

def main():
    logger.info("=== Starting Meme Coin Generator ===")
    
    try:
        trends = (
            TrendScraper.get_google_trends() +
            TrendScraper.get_reddit_memes() +
            TrendScraper.get_crypto_trends()
        )[:8]
        
        assets = []
        for trend in trends:
            name = MemeCoinGenerator.generate_hype_name(trend)
            ticker = MemeCoinGenerator.generate_ticker(name)
            assets.append((trend, name, ticker))
        
        if send_telegram_report(assets):
            logger.info("Report successfully delivered to Telegram")
        else:
            logger.warning("Report generated but Telegram delivery failed")
            
    except Exception as e:
        logger.error(f"Critical failure: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
