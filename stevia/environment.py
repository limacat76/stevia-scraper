import os
import praw
import psycopg2
import couchdb
from furl import furl


def connect_to_reddit():
    client_id = os.environ['STEVIA_PRAW_PERSONAL_USE_SCRIPT']
    client_secret = os.environ['STEVIA_PRAW_PERSONAL_USE_SECRET']
    user_agent = os.environ['STEVIA_PRAW_USER_AGENT']

    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         user_agent=user_agent
                         )

    return reddit


def connect_to_postgres():
    postgres_server = os.environ['POSTGRES_SERVER']
    postgres_port = os.environ['POSTGRES_PORT']
    postgres_user = os.environ['POSTGRES_USER']
    postgres_database = os.environ['POSTGRES_DATABASE']
    postgres_password = os.environ['POSTGRES_PASSWORD']

    conn = psycopg2.connect(
        host=postgres_server, port=postgres_port, database=postgres_database, user=postgres_user, password=postgres_password)

    return conn


def connect_to_couchdb():
    couchdb_scheme = os.environ['COUCHDB_SCHEME']
    couchdb_host = os.environ['COUCHDB_HOST']
    couchdb_port = os.environ['COUCHDB_PORT']
    couchdb_username = os.environ['COUCHDB_USER']
    couchdb_password = os.environ['COUCHDB_PASSWORD']

    couch = couchdb.Server(furl(scheme=couchdb_scheme, host=couchdb_host, port=couchdb_port,
                                username=couchdb_username, password=couchdb_password).url)

    return couch
