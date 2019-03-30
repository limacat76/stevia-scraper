import time
from . import utils as sv_utils


def sv_format_thread(subreddit_name, submission):
    couch_id = "{}-{}".format(subreddit_name, submission.fullname)
    thread = {
        "_id": couch_id,
        "stevia_type": "thread",
        "subreddit": subreddit_name,
        "reddit_id": submission.id,
        "fullname": submission.fullname,
        "is_self": submission.is_self,
        "title": submission.title,
        "score": submission.score,
        "url": submission.url,
        "created_utc": submission.created_utc,
        "permalink":  submission.permalink,
    }

    return thread, couch_id


def sv_read_all_threads_list(storage, subreddit, subreddit_name, watermark_t3, limit, max, sleep_time):
    # batch values
    last_t3 = ''
    top_t3 = ''
    first = True
    complete = False
    current = 0

    while not complete:
        if first:
            first = False
        else:
            time.sleep(sleep_time)

        if sv_utils.is_not_blank(last_t3):
            print("last_t3 not blank")
            new_subreddit = subreddit.new(
                limit=limit, params={'after': last_t3})
        elif sv_utils.is_not_blank(watermark_t3):
            print("watermark_t3 not blank")
            new_subreddit = subreddit.new(
                limit=limit, params={'before': watermark_t3})
        else:
            print("reading reddits with limit", limit)
            new_subreddit = subreddit.new(limit=limit)

        numbers = 0
        for submission in new_subreddit:
            numbers += 1
            current += 1

            if sv_utils.is_blank(top_t3):
                top_t3 = submission.fullname

            if max > 0 and current >= max:
                complete = True
                # TODO better logging
                print("*** will exit for max number reached ***")
            elif submission.fullname == watermark_t3:
                complete = True
                # TODO better logging
                print("*** reached last time limit, will not write ***")
                break

            last_t3 = submission.fullname
            # print(submission.title, submission.id,
            #      submission.fullname)

            # print("***")

            # pprint(vars(submission))
            thread, couch_id = sv_format_thread(subreddit_name, submission)

            old_doc = storage.get(couch_id)
            if old_doc is not None:
                thread["_rev"] = old_doc.rev

            storage.save(thread)
            #print(id, rev)

        if numbers == 0:
            complete = True
            # TODO better logging
            print("*** reached subreddit limit ***")

    print("elaborated ", current, "(", numbers, ") threddits")

    # TODO better logging
    print("")
    print("***")
    print(watermark_t3, top_t3)
    return top_t3
