import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def update_ts(new_last_ts):

    conn = psycopg2.connect(
        dbname=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO etl_state (id, last_processed)
            VALUES ('bars_and_cross_spread_1m', %s)
            ON CONFLICT (id) DO UPDATE
            SET last_processed = EXCLUDED.last_processed;
            """,
            (new_last_ts,),
        )

    conn.close()
    return
