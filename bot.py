import tweepy
import time
import random
import os
import threading
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

# --- Twitter API Setup ---
client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

# numerical id 
BOT_USER_ID = os.getenv("2019338817635831808")

#flask server or some bullshit (render requirement)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# --- Bot Logic ---
def get_random_phrase():
    with open("pauljac.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    return random.choice(lines).strip()

def bot_loop():
    last_mention_id = 1  
    
    while True:
        try:
            # 1. Post hourly phrase
            phrase = get_random_phrase()
            client.create_tweet(text=phrase)
            print(f"Posted: {phrase}")

            # 2. Check and Reply to Mentions
            # Note: Free tier may limit how often you can call this
            mentions = client.get_users_mentions(id=BOT_USER_ID, since_id=last_mention_id)
            
            if mentions.data:
                for tweet in mentions.data:
                    client.create_tweet(
                        text=f"{get_random_phrase()}",
                        in_reply_to_tweet_id=tweet.id
                    )
                    last_mention_id = tweet.id
                    print(f"Replied to tweet: {tweet.id}")

        except Exception as e:
            print(f"Error: {e}")

        # Sleep for 60 minutes
        time.sleep(3600)

if __name__ == "__main__":
    # Run the bot loop in a separate thread
    threading.Thread(target=bot_loop, daemon=True).start()
    # Run Flask on the port Render provides
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
