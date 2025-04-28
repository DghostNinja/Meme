import os
import random
import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import re

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
        """Scrape trending search terms"""
        try:
            url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml-xml')
            return [item.title.text for item in soup.find_all('item')[:5]]
        except Exception as e:
            logger.error(f"Google Trends failed: {str(e)}")
            return ["Bitcoin ETF", "AI Crypto", "Meme Coin", "Web3 Games", "NFT Art"]

    @staticmethod
    def get_reddit_memes():
        """Scrape trending meme topics from Reddit"""
        try:
            url = "https://www.reddit.com/r/memes/top.json?limit=5"
            data = requests.get(url, headers={'User-Agent': 'MemeScraper'}).json()
            return [post['data']['title'] for post in data['data']['children']]
        except Exception:
            return ["Doge to the moon", "WAGMI culture", "NGMI memes", "Based degeneracy", "Ape together strong"]

    @staticmethod
    def get_crypto_trends():
        """Get trending crypto topics"""
        try:
            url = "https://api.coingecko.com/api/v3/search/trending"
            data = requests.get(url).json()
            return [coin['item']['name'] for coin in data['coins'][:3]] + \
                   [nft['name'] for nft in data['nfts'][:2]]
        except Exception:
            return ["Pepe", "Wojak", "Based", "Degen", "ApeCoin"]

class MemeCoinGenerator:
    # Web3 hype components
    PREFIXES = ["Based", "Degen", "Ape", "GM", "WAGMI", "NGMI", "PEPE", "Wojak", "Smol", "Chad"]
    SUFFIXES = ["Inu", "Fi", "Swap", "Moon", "Rekt", "Maxi", "Labs", "DAO", "Farm", "Pad"]
    NUMBERS = ["69", "420", "777", "10k", "1M"]
    MEME_WORDS = ["Diamond", "Hands", "Bags", "Lambo", "Wen", "Ser", "Fren", "Copium", "Hopium"]

    @classmethod
    def generate_hype_name(cls, trend):
        """Generate Web3-hyped coin name"""
        words = [w for w in re.findall(r'\b\w{3,}\b', trend) if not w.isdigit()]
        
        if random.random() > 0.2:
            base = random.choice(cls.PREFIXES) + random.choice(["", " "])
        else:
            base = ""
        
        if words:
            base += "".join([w.capitalize() for w in words[:2]])
        else:
            base += random.choice(cls.MEME_WORDS)
        
        suffix = random.choice(cls.SUFFIXES)
        if random.random() > 0.3:
            suffix += random.choice(cls.NUMBERS)
        
        return f"{base}{suffix}"

    @classmethod
    def generate_ticker(cls, name):
        """Create exchange-style ticker"""
        clean_name = re.sub(r'\d+', '', name)
        letters = [c for c in clean_name if c.isupper() or c.islower()]
        
        if len(letters) >= 3:
            ticker = "".join(letters[:3]).upper()
        else:
            ticker = clean_name[:3].upper().ljust(3, 'X')
        
        if random.random() > 0.5:
            ticker += random.choice(cls.NUMBERS[:2])
        
        return ticker[:5]

def send_telegram_report(assets):
    """Send formatted report to Telegram"""
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
