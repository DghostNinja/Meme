# meme.py

# SSL Fix: Trust all certificates (only for testing purpose)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import snscrape.modules.twitter as sntwitter
import random
import requests
import os

# Telegram Bot Setup
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def send_to_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] Telegram credentials missing.")
        return
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(TELEGRAM_API_URL, data=payload)
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")

# Define your search query
search_query = "(breaking OR news) (world OR foreign) lang:en since:2025-04-25"
tweet_limit = 50

# Collect tweets
tweets = []

try:
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search_query).get_items()):
        if i >= tweet_limit:
            break
        tweets.append({
            'content': tweet.content,
            'date': tweet.date,
            'user': tweet.user.username,
            'url': tweet.url
        })
except Exception as e:
    send_to_telegram(f"[ERROR] Failed to scrape tweets: {e}")
    exit(1)

if not tweets:
    send_to_telegram("[INFO] No tweets found! Try adjusting the query or checking your internet.")
    exit(0)

# Send random tweets
header = "\n<b>=== Latest Foreign News Ideas for Meme Coins ===</b>\n"
send_to_telegram(header)

for tweet in random.sample(tweets, min(5, len(tweets))):
    message = (
        f"Date: {tweet['date']}\n"
        f"User: @{tweet['user']}\n"
        f"Tweet: {tweet['content']}\n"
        f"Link: {tweet['url']}\n"
        f"{'-'*30}"
    )
    send_to_telegram(message)

# Meme Coin name generator
def generate_meme_coin_name(text):
    words = text.split()
    meme_words = [w.capitalize() for w in words if len(w) > 3][:2]
    return ''.join(meme_words) + "Coin" if meme_words else "NewsMemeCoin"

send_to_telegram("\n<b>=== Suggested Meme Coin Names ===</b>\n")

for tweet in random.sample(tweets, min(5, len(tweets))):
    name = generate_meme_coin_name(tweet['content'])
    send_to_telegram(f"Meme Coin Idea: {name}")
