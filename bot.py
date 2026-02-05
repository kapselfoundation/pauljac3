import tweepy
import time
import random
import os
import threading
from flask import Flask

# --- CONFIGURATION ---
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

# --- THE BOT BRAIN ---
def get_random_phrase():
    try:
        # UPDATED FILENAME HERE
        with open("pauljac.txt", "r", encoding="utf-8") as f:
            phrases = [line.strip() for line in f if line.strip()]
        return random.choice(phrases)
    except Exception as e:
        print(f"❌ File Error (pauljac.txt): {e}")
        return "Thinking of something clever..."

def run_bot():
    print("🚀 BOT LOOP INITIALIZED")
    last_post_time = 0
    last_mention_id = 1 
    
    while True:
        now = time.time()

        # 1. Post every 90 mins (5400s)
        if now - last_post_time > 5400:
            try:
                tweet = get_random_phrase()
                client.create_tweet(text=tweet)
                print(f"✅ Posted: {tweet}")
                last_post_time = now
            except Exception as e:
                print(f"❌ Post Error: {e}")

        # 2. Check for replies every 2 mins
        try:
            mentions = client.get_users_mentions(id=BOT_USER_ID, since_id=last_mention_id)
            if mentions.data:
                for tweet in mentions.data:
                    reply = f"@{tweet.author_id} {get_random_phrase()}"
                    client.create_tweet(text=reply, in_reply_to_tweet_id=tweet.id)
                    last_mention_id = tweet.id
                    print(f"💬 Replied to tweet {tweet.id}")
        except Exception as e:
            if "429" not in str(e): 
                print(f"⚠️ Mention Error: {e}")

        time.sleep(120)

# --- STARTUP ---
print("Starting background thread...")
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
