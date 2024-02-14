##################
#                #
#     catAPI     #
#                #
##################

# yes, this is literally a copy of duckAPI.py with the subreddit changed :pepega:

import os
import asyncpraw as apraw

client_id = str(os.getenv('reddit_clientID'))
client_secret = str(os.getenv('reddit_clientSecret'))
user_agent = str(os.getenv('reddit_user_agent'))
password = str(os.getenv('reddit_password'))
username = str(os.getenv('reddit_username'))

# The reddit instance
reddit = apraw.Reddit(client_id = client_id,
                      client_secret = client_secret,
                      password = password,
                      user_agent = user_agent,
                      username = username)


async def get_image():
    # fully inizialize the list cause why not
    url_list: list = [] * 100

    # targert subreddit to get the images from
    target_subreddit = await reddit.subreddit("cats")

    # fetch subreddits
    print('getting cat images..')
    x = 0
    async for submission in target_subreddit.new(limit = 50):
        x += 1
        print(f'image number {x}')
        # put the url in a list if it ends with image extension
        if submission.url.endswith(('.jpg', '.png', '.jpeg')):
            url_list.append(submission.url)

    # return the list to use it in the command
    print('sending the images!')
    return url_list


async def get_video():
    # fully inizialize the list cause why not
    url_list: list = []

    # targert subreddit to get the videos from
    target_subreddit = await reddit.subreddit("cats")

    # fetch subreddits
    async for submission in target_subreddit.new(limit = 50):

        # check if the post (submission) is a video
        if submission.is_video:
            
            # if it is then join the reddit site with the permalink (/r/...)
            reddit_site: str = "https://www.reddit.com"
            post_url = reddit_site + submission.permalink
            # append the full link to the submission to a list
            url_list.append(post_url)

    # return the list to use it in the command
    return url_list

if __name__ == "__main__":
    print('You ran catAPI.py as standalone. Now what?')
