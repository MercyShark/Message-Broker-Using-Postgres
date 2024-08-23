import os
from psycopg2.pool import SimpleConnectionPool
from fastapi import HTTPException
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()


class Database:
    def __init__(self):
        self.pool = SimpleConnectionPool(
            minconn=os.getenv("POSTGRES_MIN_CONNECTIONS"),
            maxconn=os.getenv("POSTGRES_MAX_CONNECTIONS"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            database=os.getenv("POSTGRES_DATABASE"),
        )

    @contextmanager
    def get_connection(self):
        conn = self.pool.getconn()
        if not conn:
            raise HTTPException(
                status_code=500, detail="Unable to get a database connection"
            )
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    def release_connection(self, conn):
        self.pool.putconn(conn)

    def close_all_connections(self):
        if self.pool:
            self.pool.closeall()
