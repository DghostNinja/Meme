import os
import random
import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import re
import html

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meme_coins.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Telegram configuration
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
        """Scrape trending search terms from alternative source"""
        try:
            # Using alternative trending news API
            url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=demo"  # Replace with your API key
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
            data = response.json()
            return [article['title'] for article in data['articles'][:5]]
        except Exception as e:
            logger.error(f"News API failed: {str(e)}")
            return ["Bitcoin ETF Approved", "AI Crypto Boom", "Meme Coin Rally", "Web3 Gaming", "NFT Market Surge"]

    @staticmethod
    def get_reddit_memes():
        """Scrape trending meme topics from Reddit"""
        try:
            url = "https://www.reddit.com/r/memes/top.json?limit=5&t=day"
            headers = {'User-Agent': 'MemeCoinGenerator/1.0'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            return [post['data']['title'] for post in data['data']['children']]
        except Exception as e:
            logger.error(f"Reddit failed: {str(e)}")
            return ["Doge to the moon", "WAGMI season", "NGMI memes", "Ape together strong", "Based culture"]

    @staticmethod
    def get_crypto_trends():
        """Get trending crypto topics from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/search/trending"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            return [coin['item']['name'] for coin in data['coins'][:3]] + \
                   [nft['name'] for nft in data['nfts'][:2]]
        except Exception as e:
            logger.error(f"CoinGecko failed: {str(e)}")
            return ["Pepe", "Wojak", "Degen", "ApeCoin", "Shib"]

class MemeCoinGenerator:
    # Web3 hype components
    PREFIXES = ["Based", "Degen", "Ape", "GM", "WAGMI", "NGMI", "PEPE", "Wojak", "Smol", "Chad"]
    SUFFIXES = ["Inu", "Fi", "Swap", "Moon", "Rekt", "Maxi", "Labs", "DAO", "Farm", "Pad"]
    NUMBERS = ["69", "420", "777", "10k", "1M"]
    MEME_WORDS = ["Diamond", "Hands", "Bags", "Lambo", "Wen", "Ser", "Fren", "Copium", "Hopium"]

    @classmethod
    def generate_hype_name(cls, trend):
        """Generate Web3-hyped coin name with proper escaping"""
        trend = html.escape(trend)  # Escape HTML special chars
        words = [w for w in re.findall(r'\b\w{3,}\b', trend) if not w.isdigit()]
        
        base = random.choice(cls.PREFIXES) if random.random() > 0.2 else ""
        base += "".join([w.capitalize() for w in words[:2]]) if words else random.choice(cls.MEME_WORDS)
        
        suffix = random.choice(cls.SUFFIXES)
        if random.random() > 0.3:
            suffix += random.choice(cls.NUMBERS)
        
        return f"{base}{suffix}"

    @classmethod
    def generate_ticker(cls, name):
        """Create exchange-style ticker with proper escaping"""
        clean_name = re.sub(r'[^a-zA-Z]', '', name)
        ticker = clean_name[:3].upper().ljust(3, 'X')
        if random.random() > 0.5:
            ticker += random.choice(cls.NUMBERS[:2])
        return ticker[:5]

def escape_markdown(text):
    """Escape special MarkdownV2 characters for Telegram"""
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def send_telegram_report(assets):
    """Send properly formatted report to Telegram"""
    if not validate_telegram_credentials():
        return False

    message = "🔥 *VIRAL MEME COIN ALERTS* 🔥\n\n"
    for trend, name, ticker in assets:
        message += (
            f"📈 *Trend:* `{escape_markdown(trend)}`\n"
            f"🪙 *Coin Name:* `{escape_markdown(name)}`\n"
            f"📊 *Ticker:* `{escape_markdown(ticker)}`\n"
            f"🚀 *Pair:* `{escape_markdown(ticker)}/USDT`\n\n"
        )
    message += f"_Generated: {escape_markdown(datetime.now().strftime('%Y-%m-%d %H:%M'))}_"

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'MarkdownV2',
                'disable_web_page_preview': True
            },
            timeout=15
        )
        
        if response.status_code == 200:
            logger.info("Telegram message sent successfully!")
            return True
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
        )[:8]  # Get top 8 trends
        
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
