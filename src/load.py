"""
load.py — PostgreSQL loader.

Accepts the cleaned DataFrames produced by transform.py and bulk-inserts
them into the tables defined in sql/schema.sql using psycopg2.
"""

import psycopg2.extras
import pandas as pd
from pathlib import Path

from db import get_connection


def load_table(conn, table_name, df, columns):
    """
    Truncate a table and bulk-insert a DataFrame's rows into it.

    Parameters:
        conn (psycopg2.extensions.connection): open database connection
        table_name (str): name of the destination table
        df (pd.DataFrame): dataframe whose columns map 1:1 to `columns`
        columns (list[str]): destination column names, in the same order
            as the corresponding columns in `df`

    Returns:
        None
    """
    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]

    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table_name}")
        columns_sql = ", ".join(columns)
        psycopg2.extras.execute_values(
            cur,
            f"INSERT INTO {table_name} ({columns_sql}) VALUES %s",
            rows,
        )
    conn.commit()
    print(f"Inserted {len(rows):,} rows into {table_name}")


if __name__ == "__main__":
    ROOT_DIR = Path(__file__).resolve().parent.parent
    orders_file = ROOT_DIR / "data" / "processed" / "orders.parquet"
    monthly_file = ROOT_DIR / "data" / "processed" / "monthly_aggregates.parquet"
    rfm_file = ROOT_DIR / "data" / "processed" / "rfm.parquet"

    try:
        orders_df = pd.read_parquet(orders_file)
        monthly_df = pd.read_parquet(monthly_file)
        rfm_df = pd.read_parquet(rfm_file)

        conn = get_connection()

        orders_columns = [
            "invoice", "stock_code", "description", "quantity",
            "invoice_date", "price", "customer_id", "country", "revenue",
        ]
        orders_source = orders_df[[
            "Invoice", "StockCode", "Description", "Quantity",
            "InvoiceDate", "Price", "Customer ID", "Country", "revenue",
        ]]
        load_table(conn, "orders", orders_source, orders_columns)

        monthly_columns = ["year_month", "total_revenue", "total_orders", "unique_customers"]
        load_table(conn, "monthly_aggregates", monthly_df[monthly_columns], monthly_columns)

        rfm_columns = ["customer_id", "recency", "frequency", "monetary", "segment"]
        rfm_source = rfm_df.rename(columns={"Customer ID": "customer_id"})
        load_table(conn, "rfm", rfm_source[rfm_columns], rfm_columns)

        conn.close()
        print("Load complete.")
    except Exception as e:
        print(f"ERROR during load: {e}")
        raise
