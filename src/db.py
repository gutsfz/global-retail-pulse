"""
db.py — Database connection utilities.

Responsible for reading credentials from environment variables (.env)
and providing a reusable psycopg2 connection/cursor factory used by
load.py and any ad-hoc query scripts.
"""

import os
import psycopg2
from dotenv import load_dotenv


def get_connection():
    """
    Open a new connection to the PostgreSQL database using credentials
    from environment variables (loaded from .env).

    Expected environment variables:
        DB_HOST: database host
        DB_PORT: database port
        DB_NAME: database name
        DB_USER: database user
        DB_PASSWORD: database password

    Returns:
        psycopg2.extensions.connection: an open database connection
    """
    load_dotenv()

    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
