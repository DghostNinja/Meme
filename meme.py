# meme.py (upgraded for Telegram)

import ssl
import snscrape.modules.twitter as sntwitter
import random
import requests
import os

# SSL Fix: Trust all certificates (for GitHub Actions)
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

# === SETTINGS ===
SEARCH_QUERY = "(breaking OR news) (world OR foreign) lang:en since:2025-04-25"
TWEET_LIMIT = 50

# === TELEGRAM SETTINGS ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Bot token from env
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")      # Chat ID from env

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("[ERROR] Telegram credentials not set.")
    exit(1)

# === SCRAPE TWEETS ===
tweets = []
try:
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(SEARCH_QUERY).get_items()):
        if i >= TWEET_LIMIT:
            break
        tweets.append({
            'content': tweet.content,
            'date': tweet.date.strftime('%Y-%m-%d %H:%M'),
            'user': tweet.user.username,
            'url': tweet.url
        })
except Exception as e:
    print(f"\n[ERROR] Failed to scrape tweets: {e}")
    exit(1)

if not tweets:
    print("\n[INFO] No tweets found! Try adjusting the query or checking your internet.")
    exit(0)

# === GENERATE MEME COIN NAMES ===
def generate_meme_coin_name(text):
    words = text.split()
    meme_words = [w.capitalize() for w in words if len(w) > 3][:2]
    return ''.join(meme_words) + "Coin" if meme_words else "NewsMemeCoin"

# === PREPARE TELEGRAM MESSAGE ===
message = "📰 *Latest Foreign News Ideas for Meme Coins*\n\n"

for tweet in random.sample(tweets, min(5, len(tweets))):
    message += f"👤 *@{tweet['user']}* ({tweet['date']})\n"
    message += f"{tweet['content']}\n"
    message += f"[View Tweet]({tweet['url']})\n"
    message += "-" * 20 + "\n"

message += "\n\n*Suggested Meme Coin Names*\n\n"

for tweet in random.sample(tweets, min(5, len(tweets))):
    name = generate_meme_coin_name(tweet['content'])
    message += f"• {name}\n"

# === SEND TO TELEGRAM ===
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": message,
    "parse_mode": "Markdown",
    "disable_web_page_preview": False
}

response = requests.post(url, json=payload, verify=False)

if response.status_code == 200:
    print("[INFO] Telegram message sent successfully.")
else:
    print(f"[ERROR] Failed to send Telegram message: {response.text}")
