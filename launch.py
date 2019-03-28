#! /usr/bin/env python3
import os
import praw
import time

client_id = os.environ['STEVIA_PRAW_PERSONAL_USE_SCRIPT']
client_secret = os.environ['STEVIA_PRAW_PERSONAL_USE_SECRET']
user_agent = os.environ['STEVIA_PRAW_USER_AGENT']

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent
                     )

subreddit_name = os.environ['REDDIT_SUBREDDIT']
subreddit = reddit.subreddit(subreddit_name)

watermark_t3 = ''
stop_t3 = ''
last_t3 = ''
first = True
complete = False

while not complete:
    if first:
        first = False
    else:
        time.sleep(1)

    if last_t3 != '':
        new_subreddit = subreddit.new(limit=100, params={'after': last_t3})
    else:
        new_subreddit = subreddit.new(limit=100)

    numbers = 0
    for submission in new_subreddit:
        if watermark_t3 == '':
            watermark_t3 = submission.fullname
        if submission.fullname == stop_t3:
            complete = True
            print("*** reached last time limit ***")
            break

        numbers += 1
        last_t3 = submission.fullname
        print(submission.title, submission.id,
              submission.fullname)

        # submission.title
        # submission.score
        # submission.id
        # submission.url
        # submission.num_comments
        # submission.created
        # submission.selftext

    if numbers == 0:
        complete = True
        print("*** reached subreddit limit ***")


print("")
print("***")
print(watermark_t3, last_t3)
print("That's all folks!")
