# meme.py
import os
import random
import subprocess
import time

# === SETTINGS ===
SEARCH_QUERIES = [
    "(breaking OR news) (world OR foreign)",
    "meme OR viral OR trending (celebrity OR pop culture)",
    "(breaking OR world OR outrageous) (news OR bizarre OR funny)",
    "meme OR viral OR trending (internet OR joke OR hashtag)",
    "crypto OR bitcoin OR meme (coin OR token OR altcoin)",
    "(satire OR joke OR funny) (world OR news OR event)",
    "#meme OR #crypto OR #funny OR #news",
    "(dog OR cat OR pet) (funny OR meme OR viral)",
    "challenge OR viral OR trend (hashtag OR meme)",
    "comedy OR satire OR funny (account OR tweet)"
]
TWEET_LIMIT = 50
MAX_RETRIES = 5
RETRY_DELAY = 10

# === TELEGRAM SETTINGS ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("[ERROR] Telegram credentials not set.")
    exit(1)

# === SCRAPE TWEETS WITH SNSCRAPE ===
tweets = []

def fetch_tweets():
    for query in SEARCH_QUERIES:
        print(f"[INFO] Searching for: {query}")
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                cmd = f"snscrape --max-results {TWEET_LIMIT} --jsonl twitter-search '{query}'"
                print(f"[DEBUG] Running: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)

                if result.returncode != 0:
                    print(f"[ERROR] snscrape failed: {result.stderr}")
                    time.sleep(RETRY_DELAY)
                    continue

                lines = result.stdout.strip().split("\n")
                if not lines:
                    print("[INFO] No tweets found, trying next query...")
                    break

                for line in lines:
                    try:
                        import json
                        tweet = json.loads(line)
                        tweets.append({
                            "content": tweet.get("content", ""),
                            "user": tweet.get("user", {}).get("username", ""),
                            "url": tweet.get("url", ""),
                            "date": tweet.get("date", "")[:10],  # Format YYYY-MM-DD
                        })
                    except Exception as e:
                        print(f"[ERROR] Failed to parse tweet JSON: {e}")
                        continue

                # Minor delay between queries
                time.sleep(5)
                return tweets

            except subprocess.TimeoutExpired:
                print(f"[ERROR] snscrape timeout, retrying ({attempt}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
                continue

        print("[ERROR] Max retries reached for this query. Moving to next.")
    return None

tweets = fetch_tweets()

if not tweets:
    print("\n[INFO] No tweets found! Try adjusting the query.")
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
import requests

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
