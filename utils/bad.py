import praw
import os
from dotenv import load_dotenv


load_dotenv()
client_id = str(os.getenv('reddit_clientID'))
client_secret = str(os.getenv('reddit_clientSecret'))
user_agent = str(os.getenv('reddit_user_agent'))
password = str(os.getenv('reddit_password'))
username = str(os.getenv('reddit_username'))

print(username, client_id, user_agent, password, username, sep = ", ")





reddit = praw.Reddit(client_id = client_id,
                     client_secret = client_secret,
                     password = password,
                     user_agent = user_agent,
                     username = username)

print(reddit.user.me())