import tweepy
import os
from dotenv import load_dotenv

load_dotenv()
# Twitter API credentials
API_KEY = os.getenv('TWITTER_API_KEY')
API_SECRET = os.getenv('TWITTER_KEY_SECRET')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')


def twitConnection(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN):
    client = tweepy.Client(
        consumer_key=API_KEY, consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET,
    )
    return client

def twitConnectionv1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET):
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)

# Ensure you're using API keys and tokens from a Twitter developer App attached to a Project
client = twitConnection(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN)
client_v1 = twitConnectionv1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

msg = f'Testerino'
tags = client.get_user(username="@KevcooT_")
print(tags)


'''
myMedia = r'snapshot'

media = client_v1.simple_upload(filename=myMedia)
media_id = media.media_id
print(media_id)

response = client.create_tweet(text=msg,media_ids=[media_id],)
print(f"Tweet with media posted successfully: {response}")
'''