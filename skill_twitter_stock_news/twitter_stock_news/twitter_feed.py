import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import tweepy
from dotenv import load_dotenv

# Load credentials from .env in the same directory as this script
load_dotenv(Path(__file__).parent / ".env")

CONSUMER_KEY = os.environ["TWITTER_API_KEY"]
CONSUMER_SECRET = os.environ["TWITTER_API_SECRET"]
ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

# Initialize Tweepy for X API v2
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)


def fetch_home_feed_recent():
    # 1. Calculate the 2-hour window in UTC
    two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2, seconds=30)
    start_str = two_hours_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        # 2. Call get_home_timeline
        # expansions=['author_id'] allows us to get the actual usernames
        response = client.get_home_timeline(
            start_time=start_str,
            max_results=100,
            tweet_fields=["created_at", "text"],
            expansions=["author_id"],
            user_fields=["username"],
        )

        if not response.data:
            print(f"No new posts in your feed since {start_str}.")
            return []

        # 3. Create a lookup dictionary for usernames
        users = {u.id: u.username for u in response.includes["users"]}

        feed_data = []
        for tweet in response.data:
            username = users.get(tweet.author_id, "Unknown")
            content = f"From @{username}: {tweet.text}"
            feed_data.append(content)
            print(f"[{tweet.created_at}] {content}\n")

        return feed_data

    except tweepy.Forbidden:
        print(
            "Error 403: Your API Tier (likely 'Free') does not allow access to the Home Timeline."
        )
        print(
            "You can still use 'get_users_tweets' to get your own posts for free."
        )
    except Exception as e:
        print(f"Error: {e}")
        return []


if __name__ == "__main__":
    recent_posts = fetch_home_feed_recent()
