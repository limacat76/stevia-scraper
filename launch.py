#! /usr/bin/env python3
import os
from pprint import pprint
from stevia import sql as sv_sql
from stevia import couchdb as sv_couchdb
from stevia import utils as sv_utils
from stevia import scraper as sv_scraper
from stevia import environment as sv_environment

# TODO MY FUNCTIONS


def main():
    reddit = sv_environment.connect_to_reddit()
    print(reddit.auth.limits)

    conn = sv_environment.connect_to_postgres()

    couch = sv_environment.connect_to_couchdb()

    couchdb_database = os.environ['COUCHDB_DATABASE']
    storage = sv_couchdb.open_or_create(couchdb_database, couch)

    sv_scraper.read_latest_threads(conn, reddit, storage)
    sv_scraper.read_old_posts(conn, reddit, storage)
    print("That's all folks!")


print(__name__)

if __name__ == '__main__':
    main()
