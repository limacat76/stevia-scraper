def read_sv_configuration(conn, key, default=''):
    with conn.cursor() as cursor:
        cursor.execute(
            'select value from sv_configuration where key = %s', (key,))
        value = cursor.fetchone()
        if value == None:
            return default
        else:
            return value[0]


def read_sv_first_job(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            'select subreddit, watermark from sv_job ')
        value = cursor.fetchone()
        if value == None:
            return None, None
        else:
            return value[0], value[1]


def write_sv_watermark(subreddit, watermark, conn):
    with conn.cursor() as cursor:
        cursor.execute(
            'update sv_job set watermark = %s where subreddit = %s', (watermark, subreddit,))
        conn.commit()
        return
