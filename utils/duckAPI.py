import os
import praw
from dotenv import load_dotenv

load_dotenv()
client_id = str(os.getenv('reddit_clientID'))
client_secret = str(os.getenv('reddit_clientSecret'))
user_agent = str(os.getenv('reddit_user_agent'))
password = str(os.getenv('reddit_password'))
username = str(os.getenv('reddit_username'))

target_subreddit = 'duck'

reddit = praw.Reddit(client_id = client_id,
                     client_secret = client_secret,
                     password = password,
                     user_agent = user_agent,
                     username = username)
                     
for submission in reddit.subreddit(target_subreddit).new(limit = 10):
    url = submission.url
    if url.endswith(('.jpg', '.png', '.jpeg')):
        print(url)