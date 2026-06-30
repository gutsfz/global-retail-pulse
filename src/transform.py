"""
transform.py — Data cleaning and feature engineering.

Takes the raw DataFrame from extract.py and applies:
  - Null removal and type coercion
  - Cancellation / negative-quantity filtering
  - Derived columns: TotalPrice, InvoiceMonth
  - RFM (Recency, Frequency, Monetary) customer segmentation
  - Monthly revenue aggregates for trend analysis

Returns cleaned DataFrames ready to be loaded into PostgreSQL.
"""

import pandas as pd
from pathlib import Path


def clean_data(df):
    """
    Clean the raw Online Retail II dataframe.

    Parameters:
        df (pd.DataFrame): raw dataframe loaded from extract.py

    Returns:
        pd.DataFrame: cleaned dataframe
    """
    print("Cleaning data...")
    rows_start = len(df)

    df = df[~df["Invoice"].astype(str).str.startswith("C")]
    rows_after_cancellations = len(df)
    print(f"  Removed cancelled orders : {rows_start - rows_after_cancellations:,}")

    df = df[df["Quantity"] > 0]
    rows_after_quantity = len(df)
    print(f"  Removed Quantity <= 0    : {rows_after_cancellations - rows_after_quantity:,}")

    df = df[df["Price"] > 0]
    rows_after_price = len(df)
    print(f"  Removed Price <= 0       : {rows_after_quantity - rows_after_price:,}")

    # Null Customer ID is filled with "Guest" instead of dropped: these rows
    # still represent real revenue (e.g. guest checkout transactions), and
    # discarding them would understate total sales in downstream aggregates.
    null_customers = df["Customer ID"].isna().sum()
    df["Customer ID"] = df["Customer ID"].fillna("Guest")
    print(f"  Filled null Customer IDs : {null_customers:,} (set to \"Guest\")")

    rows_before_duplicates = len(df)
    df = df.drop_duplicates()
    rows_after_duplicates = len(df)
    print(f"  Removed duplicate rows   : {rows_before_duplicates - rows_after_duplicates:,}")

    print("Cleaning summary:")
    print(f"  Rows before : {rows_start:,}")
    print(f"  Rows after  : {rows_after_duplicates:,}")
    print(f"  Total removed : {rows_start - rows_after_duplicates:,}")

    return df


def add_revenue(df):
    """
    Add a revenue column computed from Quantity and Price.

    Parameters:
        df (pd.DataFrame): cleaned dataframe

    Returns:
        pd.DataFrame: dataframe with an added "revenue" column
    """
    print("Adding revenue column...")
    df["revenue"] = df["Quantity"] * df["Price"]
    return df


def build_monthly_aggregates(df, output_path):
    """
    Build monthly revenue and order aggregates.

    Parameters:
        df (pd.DataFrame): cleaned dataframe with a "revenue" column
        output_path (Path): destination .parquet file path

    Returns:
        pd.DataFrame: dataframe aggregated by year_month
    """
    print("Building monthly aggregates...")
    df = df.copy()

    df["year_month"] = df["InvoiceDate"].dt.strftime("%Y-%m")
    print(f"  year_month range: {df['year_month'].min()} to {df['year_month'].max()}")

    non_guest = df[df["Customer ID"] != "Guest"]
    unique_customers = non_guest.groupby("year_month")["Customer ID"].nunique()

    monthly = df.groupby("year_month").agg(
        total_revenue=("revenue", "sum"),
        total_orders=("Invoice", "nunique"),
    )
    monthly["unique_customers"] = unique_customers
    monthly["unique_customers"] = monthly["unique_customers"].fillna(0).astype(int)
    monthly = monthly.reset_index()
    print(f"  Generated {len(monthly):,} unique months")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    monthly.to_parquet(output_path, index=False)
    print(f"Monthly aggregates saved to {output_path} ({len(monthly):,} months)")

    return monthly


def build_rfm(df, output_path):
    """
    Build a Recency, Frequency, Monetary (RFM) table per customer.

    Parameters:
        df (pd.DataFrame): cleaned dataframe with a "revenue" column
        output_path (Path): destination .parquet file path

    Returns:
        pd.DataFrame: dataframe with RFM metrics and segment per Customer ID
    """
    print("Building RFM analysis...")
    df = df.copy()

    # Exclude "Guest" customers: RFM segmentation requires a stable customer
    # identity to track recency/frequency/monetary across orders over time.
    known = df[df["Customer ID"] != "Guest"]
    print(f"  Known customers (excluding Guest): {known['Customer ID'].nunique():,}")

    snapshot_date = known["InvoiceDate"].max() + pd.Timedelta(days=1)
    print(f"  Snapshot date: {snapshot_date}")

    rfm = known.groupby("Customer ID").agg(
        recency=("InvoiceDate", lambda dates: (snapshot_date - dates.max()).days),
        frequency=("Invoice", "nunique"),
        monetary=("revenue", "sum"),
    ).reset_index()
    print(f"  RFM rows computed: {len(rfm):,} unique customers")

    def assign_segment(row):
        """Assign a customer segment using simple, ordered RFM thresholds."""
        # VIP and Loyal are checked first since they depend on frequency and
        # monetary value, taking priority over recency-based segments.
        if row["frequency"] >= 10 and row["monetary"] >= 1000:
            return "VIP"
        if row["frequency"] >= 5 and row["monetary"] >= 500:
            return "Loyal"
        if row["recency"] <= 90:
            return "New"
        if row["recency"] <= 180:
            return "At Risk"
        return "Lost"

    rfm["segment"] = rfm.apply(assign_segment, axis=1)
    print("  Segment counts:")
    print(rfm["segment"].value_counts().to_string())

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rfm.to_parquet(output_path, index=False)
    print(f"RFM analysis saved to {output_path} ({len(rfm):,} customers)")

    return rfm


if __name__ == "__main__":
    ROOT_DIR = Path(__file__).resolve().parent.parent
    raw_file = ROOT_DIR / "data" / "raw" / "online_retail_II.parquet"
    monthly_file = ROOT_DIR / "data" / "processed" / "monthly_aggregates.parquet"
    rfm_file = ROOT_DIR / "data" / "processed" / "rfm.parquet"

    try:
        df = pd.read_parquet(raw_file)
        print(f"Loaded {len(df):,} rows from parquet")
    except Exception as e:
        print(f"ERROR loading parquet: {e}")
        raise

    try:
        df = clean_data(df)
    except Exception as e:
        print(f"ERROR in clean_data: {e}")
        raise

    try:
        df = add_revenue(df)
    except Exception as e:
        print(f"ERROR in add_revenue: {e}")
        raise

    try:
        build_monthly_aggregates(df, monthly_file)
    except Exception as e:
        print(f"ERROR in build_monthly_aggregates: {e}")
        raise

    try:
        build_rfm(df, rfm_file)
    except Exception as e:
        print(f"ERROR in build_rfm: {e}")
        raise

    print("Transformation complete.")
