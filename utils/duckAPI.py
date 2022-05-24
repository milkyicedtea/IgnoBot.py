import praw

client_id = str(os.getenv(reddit_clientID))
client_secret = str(os.getenv(reddit_clientSecret))
user_agent = str(os.getenv(reddit_user))

target_subreddit = 'duck'

reddit = praw.Reddit(client_id = client_id,
                     client_secret = client_secret, 
                     user_agent = user_agent)
                     
for submission in reddit.subreddit(target_subreddit).new(limit = 1):
    url = submission.url
    if url.endswith(('.jpg', '.png', '.gif', '.jpeg')):
        print(url)