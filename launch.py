#! /usr/bin/env python3
import os
import time
import datetime
from pprint import pprint
from stevia import sql as sv_sql
from stevia import couchdb as sv_couchdb
from stevia import utils as sv_utils
from stevia import scraper as sv_scraper
from stevia import environment as sv_environment

# TODO MY FUNCTIONS


def read_latest_threads(conn, reddit, storage):
    subreddit_name, watermark_t3 = sv_sql.read_sv_first_job(conn)

    if subreddit_name == None:
        # TODO better logging
        print("*** no job defined, skipping threads reading ***")
        return

    # TODO better logging
    print("*** working on: ", subreddit_name, watermark_t3)

    sleep_time = int(sv_sql.read_sv_configuration(
        'STEVIA_SLEEP_TIME', conn))
    limit = int(sv_sql.read_sv_configuration('REDDIT_RATE_LIMIT', conn))

    print("scraper sleep time:", sleep_time)
    print("reddit limit: ", limit)

    # TODO read from job definition?
    max = 0
    couch_boom = sv_utils.str_2_bool(
        sv_sql.read_sv_configuration('DEBUG_COUCH_DB_WRITE', conn))
    if couch_boom:
        print(
            "DEBUG_COUCH_DB_WRITE is true, limiting access to the current job to the first record")
        limit = 1
        max = 1
        watermark_t3 = ''

    subreddit = reddit.subreddit(subreddit_name)

    print(reddit.auth.limits)

    top_t3 = sv_scraper.sv_read_all_threads_list(
        storage, subreddit, subreddit_name, watermark_t3, limit, max, sleep_time)

    if not couch_boom and sv_utils.is_not_blank(top_t3):
        sv_sql.write_sv_watermark(subreddit_name, top_t3, conn)
    else:
        print("not storing t3 because couch_boom ",
              couch_boom, " or blank t3 (", top_t3, ")")


def main():
    reddit = sv_environment.connect_to_reddit()
    print(reddit.auth.limits)

    conn = sv_environment.connect_to_postgres()

    couch = sv_environment.connect_to_couchdb()

    couchdb_database = os.environ['COUCHDB_DATABASE']
    storage = sv_couchdb.open_or_create(couchdb_database, couch)

    read_latest_threads(conn, reddit, storage)
    print("Now read all files older than one week...")

    # doc_start = 0
    # week_before = int(datetime.datetime.utcnow(
    # ).timestamp() - 60 * 60 * 24 * 7)
    # for y in storage.view('threads/unread_subreddit_time')[['stadia', doc_start]:['stadia', week_before]]:
    #    print(y)

    print("Limits?")

    print(reddit.auth.limits)

    print("That's all folks!")


print(__name__)

if __name__ == '__main__':
    main()
