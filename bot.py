import tweepy
import time
import random
import os
import threading
import sys
from flask import Flask

# --- 1. CONFIGURATION ---
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
BOT_USER_ID = os.getenv("BOT_USER_ID")

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is alive and watching pauljac.txt!", 200

# --- 2. THE BOT BRAIN ---
def get_random_phrase():
    try:
        with open("pauljac.txt", "r", encoding="utf-8") as f:
            phrases = [line.strip() for line in f if line.strip()]
        if not phrases:
            return "The pauljac.txt file is empty!"
        return random.choice(phrases)
    except Exception as e:
        # flush=True forces this to show up in Render logs immediately
        print(f"❌ File Error (pauljac.txt): {e}", flush=True)
        return "Checking the logs for errors..."

def run_bot():
    # Force logs to show startup
    print("🚀 BOT LOOP INITIALIZED", flush=True)
    last_post_time = 0
    last_mention_id = None 
    
    while True:
        now = time.time()

        # A. Post a random phrase every 90 minutes
        if now - last_post_time > 5400:
            try:
                tweet = get_random_phrase()
                client.create_tweet(text=tweet)
                print(f"✅ Posted: {tweet}", flush=True)
                last_post_time = now
            except Exception as e:
                print(f"❌ Post Error: {e}", flush=True)

        # B. Check for replies every 2 minutes
        try:
            mentions = client.get_users_mentions(id=BOT_USER_ID, since_id=last_mention_id)
            if mentions.data:
                for tweet in mentions.data:
                    reply = f"@{tweet.author_id} {get_random_phrase()}"
                    client.create_tweet(text=reply, in_reply_to_tweet_id=tweet.id)
                    last_mention_id = tweet.id
                    print(f"💬 Replied to tweet {tweet.id}", flush=True)
        except Exception as e:
            # We ignore 429 (Rate Limit) errors for mentions to keep logs clean
            if "429" not in str(e): 
                print(f"⚠️ Mention Error: {e}", flush=True)

        time.sleep(120)

# --- 3. STARTUP ---
# Start the background thread before Flask starts
print("Starting background thread...", flush=True)
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
