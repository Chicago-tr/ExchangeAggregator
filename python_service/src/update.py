import sys

import psycopg2
from psycopg2.extras import execute_values

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "arb"


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
