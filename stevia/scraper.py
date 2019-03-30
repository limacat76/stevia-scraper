import time
import datetime
from pprint import pprint
from . import sql as sv_sql
from . import utils as sv_utils


def sv_format_comment(subreddit_name, thread, comment):
    thread = sv_utils.to_dict(thread)
    comment = sv_utils.to_dict(comment)

    t_id = thread["id"]
    c_id = comment["id"]

    couch_id = "{}-{}-{}".format(subreddit_name,
                                 thread["id"], comment["id"])

    if t_id == c_id and comment["is_self"]:
        comment["text"] = comment["selftext"]
        comment = sv_utils.extract(comment, ["id", "fullname", "text"])
    else:
        comment["text"] = comment["body"]
        comment = sv_utils.extract(comment, ["id", "fullname", "text"])

    comment["_id"] = couch_id
    comment["sv_subreddit_name"] = subreddit_name
    comment["sv_type"] = "reddit_comment"
    comment["sv_thread_id"] = thread["id"]

    return comment, couch_id


def sv_format_thread(subreddit_name, submission):
    couch_id = "{}-{}".format(subreddit_name, submission.id)
    thread = sv_utils.extract(sv_utils.to_dict(submission), [
        "id", "fullname", "is_self", "title", "score", "url", "created_utc", "permalink"])
    thread["_id"] = couch_id
    thread["sv_type"] = "reddit_thread"
    thread["sv_subreddit_name"] = subreddit_name

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

            # TODO ABSTRACT
            thread, couch_id = sv_format_thread(subreddit_name, submission)

            old_doc = storage.get(couch_id)
            if old_doc is not None:
                thread["_rev"] = old_doc.rev

            storage.save(thread)
            # print(id, rev)

            if submission.is_self:
                comment, couch_id = sv_format_comment(
                    subreddit_name, submission, submission)
                pprint(comment)
                old_doc = storage.get(couch_id)
                if old_doc is not None:
                    comment["_rev"] = old_doc.rev

                storage.save(comment)

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


def read_latest_threads(conn, reddit, storage):
    # TODO loop on job definitions
    subreddit_name, watermark_t3 = sv_sql.read_sv_first_job(conn)

    if subreddit_name == None:
        # TODO better logging
        print("*** no job defined, skipping threads reading ***")
        return

    # TODO better logging
    print("*** working on: ", subreddit_name, watermark_t3)

    sleep_time = int(sv_sql.read_sv_configuration(
        conn, 'STEVIA_SLEEP_TIME', 2))
    limit = int(sv_sql.read_sv_configuration(conn, 'REDDIT_RATE_LIMIT', 100))

    print("scraper sleep time:", sleep_time)
    print("reddit limit: ", limit)

    # TODO read from job definition?
    max = 0
    couch_boom = sv_utils.str_2_bool(
        sv_sql.read_sv_configuration(conn, 'DEBUG_COUCH_DB_WRITE', 'false'))
    if couch_boom:
        print(
            "DEBUG_COUCH_DB_WRITE is true, limiting access to the current job to the first record")
        max = int(sv_sql.read_sv_configuration(
            conn, 'DEBUG_COUCH_DB_THREADS', '1'))
        limit = max
        watermark_t3 = ''

    subreddit = reddit.subreddit(subreddit_name)

    print(reddit.auth.limits)

    top_t3 = sv_read_all_threads_list(
        storage, subreddit, subreddit_name, watermark_t3, limit, max, sleep_time)

    if not couch_boom and sv_utils.is_not_blank(top_t3):
        sv_sql.write_sv_watermark(subreddit_name, top_t3, conn)
    else:
        print("not storing t3 because couch_boom ",
              couch_boom, " or blank t3 (", top_t3, ")")


def read_old_posts(conn, reddit, storage):
    # TODO loop on job definitions
    subreddit_name, _ = sv_sql.read_sv_first_job(conn)

    print("Now read all comments older than one week...")

    block_me = False
    doc_start = 0
    week_before = int(
        datetime.datetime.utcnow().timestamp() - 60 * 60 * 24 * 7)
    for y in storage.view('threads/unread_subreddit_time')[[subreddit_name, doc_start]:[subreddit_name, week_before]]:
        time.sleep(2)

        reddit_id = y.value['id']
        sv_submission = storage[y.id]

        submission = reddit.submission(id=reddit_id)
        submission.comments.replace_more(limit=None)

        print("the thread")
        # pprint(sv_submission)
        print(reddit_id)

        for comment in submission.comments.list():
            print("*a post*")
            post, _ = sv_format_comment(
                subreddit_name, sv_submission, comment)
            # pprint(post)
            print(post["id"])
            storage.save(post)
            # print(comment.fullname)
            # print(comment.body)

        print("submission downloaded")
        sv_submission['sv_downloaded'] = 'true'
        storage.save(sv_submission)

        if block_me:
            print("early exit")
            quit()
        # print(y.value)
        # print(submission)
