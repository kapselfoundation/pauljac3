import tweepy
import random
import time
import os

# ---------- CONFIG ----------
PHRASES_FILE = "pauljac.txt"
LAST_ID_FILE = "last_replied_id.txt"
POST_INTERVAL = 60 * 60  # 1 hour
MENTION_CHECK_INTERVAL = 5 * 60  # 5 minutes
# ----------------------------

def load_phrases():
    with open(PHRASES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

phrases = load_phrases()

client = tweepy.Client(
    bearer_token=os.environ["BEARER_TOKEN"],
    consumer_key=os.environ["X_API_KEY"],
    consumer_secret=os.environ["X_API_SECRET"],
    access_token=os.environ["X_ACCESS_TOKEN"],
    access_token_secret=os.environ["X_ACCESS_SECRET"],
    wait_on_rate_limit=True
)

BOT_USER_ID = os.environ["BOT_USER_ID"]

def random_phrase():
    return random.choice(phrases)

def get_last_id():
    if os.path.exists(LAST_ID_FILE):
        return int(open(LAST_ID_FILE).read().strip())
    return None

def save_last_id(tweet_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(tweet_id))

def post_random_tweet():
    client.create_tweet(text=random_phrase())
    print("Posted tweet")

def reply_to_mentions():
    since_id = get_last_id()

    mentions = client.get_users_mentions(
        id=BOT_USER_ID,
        since_id=since_id,
        max_results=10
    )

    if not mentions.data:
        return

    for tweet in reversed(mentions.data):
        # skip self-replies just in case
        if str(tweet.author_id) == BOT_USER_ID:
            continue

        client.create_tweet(
            text=random_phrase(),
            in_reply_to_tweet_id=tweet.id
        )
        print(f"Replied to {tweet.id}")
        save_last_id(tweet.id)
        time.sleep(random.randint(10, 30))  # anti-spam delay

if __name__ == "__main__":
    last_post = 0
    last_check = 0

    while True:
        now = time.time()

        if now - last_post > POST_INTERVAL:
            post_random_tweet()
            last_post = now

        if now - last_check > MENTION_CHECK_INTERVAL:
            reply_to_mentions()
            last_check = now

        time.sleep(10)
