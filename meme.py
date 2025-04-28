# meme.py (Nitter Version for Telegram)

import ssl
import requests
import random
import os
from bs4 import BeautifulSoup
import urllib.parse

# SSL Fix: Trust all certificates (for GitHub Actions)
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

# === SETTINGS ===
NITTER_BASE_URL = "https://nitter.privacydev.net"
SEARCH_QUERY = "(breaking OR news) (world OR foreign)"
TWEET_LIMIT = 50

# === TELEGRAM SETTINGS ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("[ERROR] Telegram credentials not set.")
    exit(1)

# === SCRAPE TWEETS ===
tweets = []

try:
    search_url = f"{NITTER_BASE_URL}/search?f=tweets&q={urllib.parse.quote_plus(SEARCH_QUERY)}&e-nativeretweets=on"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers, verify=False)

    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch tweets: {response.status_code}")
        exit(1)

    soup = BeautifulSoup(response.text, "html.parser")
    tweet_elements = soup.find_all("div", class_="timeline-item")

    for elem in tweet_elements[:TWEET_LIMIT]:
        content_elem = elem.find("div", class_="tweet-content")
        user_elem = elem.find("a", class_="username")
        date_elem = elem.find("span", class_="tweet-date")
        link_elem = date_elem.find("a") if date_elem else None

        if content_elem and user_elem and link_elem:
            tweets.append({
                "content": content_elem.text.strip(),
                "user": user_elem.text.strip().lstrip("@"),
                "url": NITTER_BASE_URL + link_elem.get("href"),
                "date": date_elem.text.strip()
            })

except Exception as e:
    print(f"\n[ERROR] Failed to scrape tweets: {e}")
    exit(1)

if not tweets:
    print("\n[INFO] No tweets found! Try adjusting the query or checking the Nitter instance.")
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
