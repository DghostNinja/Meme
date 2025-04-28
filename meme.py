# meme.py (upgraded for Reddit/Google News, no SSL issues)

import requests
import os
import random

# === SETTINGS ===
REDDIT_URL = "https://www.reddit.com/r/worldnews/hot.json?limit=50"
HEADERS = {"User-Agent": "Mozilla/5.0"}  # pretend to be a browser

# === TELEGRAM SETTINGS ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Bot token from env
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")      # Chat ID from env

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("[ERROR] Telegram credentials not set.")
    exit(1)

# === SCRAPE REDDIT POSTS ===
try:
    response = requests.get(REDDIT_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()
    data = response.json()
    posts = data["data"]["children"]
except Exception as e:
    print(f"[ERROR] Failed to fetch Reddit posts: {e}")
    exit(1)

if not posts:
    print("[INFO] No posts found.")
    exit(0)

# === GENERATE MEME COIN NAMES ===
def generate_meme_coin_name(text):
    words = text.split()
    meme_words = [w.capitalize() for w in words if len(w) > 3][:2]
    return ''.join(meme_words) + "Coin" if meme_words else "NewsMemeCoin"

# === PREPARE TELEGRAM MESSAGE ===
message = "📰 *Latest Foreign News Ideas for Meme Coins*\n\n"

for post in random.sample(posts, min(5, len(posts))):
    title = post["data"]["title"]
    url = "https://reddit.com" + post["data"]["permalink"]
    message += f"📰 *{title}*\n"
    message += f"[View Post]({url})\n"
    message += "-" * 20 + "\n"

message += "\n\n*Suggested Meme Coin Names*\n\n"

for post in random.sample(posts, min(5, len(posts))):
    title = post["data"]["title"]
    name = generate_meme_coin_name(title)
    message += f"• {name}\n"

# === SEND TO TELEGRAM ===
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": message,
    "parse_mode": "Markdown",
    "disable_web_page_preview": False
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("[INFO] Telegram message sent successfully.")
else:
    print(f"[ERROR] Failed to send Telegram message: {response.text}")
