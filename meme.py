import os
import random
import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram config
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

class TrendScraper:
    @staticmethod
    def get_google_trends():
        """Scrape trending search terms"""
        try:
            url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
            soup = BeautifulSoup(requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).content, 'lxml-xml')
            return [item.title.text for item in soup.find_all('item')[:5]]
        except Exception:
            return ["Bitcoin ETF", "Solana Phone", "AI Crypto", "Meme Coin Rally", "NFT Gaming"]

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
        # Clean the trend text
        words = [w for w in re.findall(r'\b\w{3,}\b', trend) if not w.isdigit()]
        
        # 80% chance to add Web3 prefix
        if random.random() > 0.2:
            base = random.choice(cls.PREFIXES) + random.choice(["", " "])
        else:
            base = ""
        
        # Build main name (mix trend words with meme words)
        if words:
            base += "".join([w.capitalize() for w in words[:2]])
        else:
            base += random.choice(cls.MEME_WORDS)
        
        # Add suffix and number
        suffix = random.choice(cls.SUFFIXES)
        if random.random() > 0.3:  # 70% chance for number
            suffix += random.choice(cls.NUMBERS)
        
        return f"{base}{suffix}"

    @classmethod
    def generate_ticker(cls, name):
        """Create exchange-style ticker"""
        # Remove numbers first
        clean_name = re.sub(r'\d+', '', name)
        letters = [c for c in clean_name if c.isupper() or c.islower()]
        
        # Build 3-5 letter ticker
        if len(letters) >= 3:
            ticker = "".join(letters[:3]).upper()
        else:
            ticker = clean_name[:3].upper().ljust(3, 'X')
        
        # 50% chance to add number
        if random.random() > 0.5:
            ticker += random.choice(cls.NUMBERS[:2])
        
        return ticker[:5]

def send_telegram_report(assets):
    """Send formatted report to Telegram"""
    message = "🔥 *VIRAL MEME COIN FACTORY* 🔥\n\n"
    message += "⚡ *Trending Right Now:* ⚡\n\n"
    
    for trend, name, ticker in assets:
        message += f"📈 *Trend:* `{trend}`\n"
        message += f"🪙 *Coin Name:* `{name}`\n"
        message += f"📊 *Ticker:* `{ticker}`\n"
        message += f"💸 *Pair:* `{ticker}/USDT`\n"
        message += f"🚀 *Potential:* `{random.randint(10,100)}x`\n\n"
    
    message += f"_Generated at {datetime.now().strftime('%Y-%m-%d %H:%M')}_"
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'MarkdownV2',
                'disable_web_page_preview': True
            }
        )
    except Exception as e:
        logger.error(f"Telegram error: {e}")

def main():
    try:
        # Get all trending content
        trends = (
            TrendScraper.get_google_trends() + 
            TrendScraper.get_reddit_memes() + 
            TrendScraper.get_crypto_trends()
        )[:8]  # Get top 8 trends
        
        # Generate coin assets
        assets = []
        for trend in trends:
            name = MemeCoinGenerator.generate_hype_name(trend)
            ticker = MemeCoinGenerator.generate_ticker(name)
            assets.append((trend, name, ticker))
        
        # Send report
        send_telegram_report(assets)
        logger.info("Generated viral coin ideas")
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
