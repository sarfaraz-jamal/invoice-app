import os
from collections.abc import Generator

from dotenv import load_dotenv
from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from the .env file.")


pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    open=True,
    kwargs={
        "row_factory": dict_row,
    },
)


def get_connection() -> Generator[Connection, None, None]:
    with pool.connection() as connection:
        yield connection