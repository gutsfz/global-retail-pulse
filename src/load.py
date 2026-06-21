"""
load.py — PostgreSQL loader.

Accepts the cleaned DataFrames produced by transform.py and bulk-inserts
them into the tables defined in sql/schema.sql using psycopg2.
Handles upserts and truncate-reload strategies depending on the target table.

Implementation added in Phase 3.
"""
