def read_sv_configuration(conn, key, default=''):
    with conn.cursor() as cursor:
        cursor.execute(
            'select value from sv_configuration where key = %s', (key,))
        value = cursor.fetchone()
        if value == None:
            return default
        else:
            return value[0]


def read_sv_jobs(conn, job_type):
    with conn.cursor() as cursor:
        cursor.execute(
            "select subreddit, watermark from sv_job where job_type = %s", (job_type, ))

        result = []
        for row in cursor:
            result.append((row[0], row[1]))

        return result


def read_sv_active_corpus_jobs(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """
                select 
                    subreddit, 
                    watermark, 
                    (threads - coalesce(read_threads, 0)) to_read
                from 
                    sv_job
                where
                    job_type = 'corpus'
                and ( 
                    read_threads is null
                    or read_threads < threads
                )
            """)

        result = []
        for row in cursor:
            print(type(row[1]))
            result.append((row[0], row[1], row[2]))

        return result


def write_sv_watermark(subreddit, watermark, conn):
    with conn.cursor() as cursor:
        cursor.execute(
            'update sv_job set watermark = %s where subreddit = %s', (watermark, subreddit,))
        conn.commit()
        return


def write_sv_threads(subreddit, watermark, read_threads, conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """
                update 
                    sv_job 
                set 
                    watermark = %s, 
                    read_threads = %s + coalesce(read_threads, 0)
                where
                    subreddit = %s
            """,
            (watermark, read_threads, subreddit,))
        conn.commit()
        return
