"""
db.py — Database connection utilities.

Responsible for reading credentials from environment variables (.env)
and providing a reusable psycopg2 connection/cursor factory used by
load.py and any ad-hoc query scripts.

Implementation added in Phase 3.
"""
