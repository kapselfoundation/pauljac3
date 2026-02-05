import tweepy
import time
import random
import os
import threading
from flask import Flask

# --- 1. CONFIGURATION ---
# These are pulled from Render's Environment Variables
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
BOT_USER_ID = os.getenv("BOT_USER_ID")

# Initialize Tweepy Client (v2 API)
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# --- 2. WEB SERVER (To keep Render alive) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is alive!", 200

# --- 3. BOT LOGIC ---
def get_random_phrase():
    try:
        with open("phrases.txt", "r", encoding="utf-8") as f:
            phrases = [line.strip() for line in f if line.strip()]
        return random.choice(phrases)
    except Exception as e:
        print(f"Error reading phrases: {e}")
        return "Thinking of something clever..."

def run_bot():
    print("Bot loop started...")
    last_responded_id = None
    
    while True:
        try:
            # POST A RANDOM PHRASE
            new_tweet = get_random_phrase()
            client.create_tweet(text=new_tweet)
            print(f"✅ Posted: {new_tweet}")

            # CHECK MENTIONS & REPLY
            # The Free Tier allows checking mentions roughly every 15 mins.
            # We check right after we post.
            mentions = client.get_users_mentions(id=BOT_USER_ID, since_id=last_responded_id)
            
            if mentions.data:
                for tweet in mentions.data:
                    reply_text = f"@{tweet.author_id} {get_random_phrase()}"
                    client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet.id)
                    last_responded_id = tweet.id
                    print(f"💬 Replied to tweet {tweet.id}")

        except Exception as e:
            print(f"❌ Error in bot loop: {e}")

        # Sleep for 90 minutes (5400 seconds) to stay under the 500 post/mo limit
        time.sleep(5400)

if __name__ == "__main__":
    # Start the bot in the background
    threading.Thread(target=run_bot, daemon=True).start()
    # Start the web server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
