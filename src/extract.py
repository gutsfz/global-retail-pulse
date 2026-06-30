import sys
import pandas as pd
from pathlib import Path

def load_raw_data(filepath):
    """
    Load the Online Retail II dataset from a CSV file.

    Parameters:
        filepath (Path): path to the raw .csv file

    Returns:
        pd.DataFrame: dataframe with all transactions
    """
    print("Loading raw data...")
    df = pd.read_csv(filepath, dtype={"Customer ID": str}, encoding="latin-1")
    print(f"Raw data loaded: {len(df):,} rows total")
    return df

def validate_dataframe(df):
    """
    Validate the dataframe structure and print a summary report.

    Parameters:
        df (pd.DataFrame): raw concatenated dataframe

    Raises:
        ValueError: if any expected column is missing

    Returns:
        None
    """
    expected_columns = [
        "Invoice", "StockCode", "Description",
        "Quantity", "InvoiceDate", "Price",
        "Customer ID", "Country"
    ]

    missing = set(expected_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    cancelled = df["Invoice"].astype(str).str.startswith("C").sum()
    null_customers = df["Customer ID"].isna().sum()
    date_min = df["InvoiceDate"].min()
    date_max = df["InvoiceDate"].max()

    print("Validation summary:")
    print(f"  Total rows        : {len(df):,}")
    print(f"  Null Customer IDs : {null_customers:,}")
    print(f"  Cancelled orders  : {cancelled:,}")
    print(f"  Date range        : {date_min} → {date_max}")

def save_parquet(df, output_path):
    """
    Save the dataframe to Parquet format.

    Parameters:
        df (pd.DataFrame): dataframe to persist
        output_path (Path): destination .parquet file path

    Returns:
        None
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"Data saved to {output_path}")


if __name__ == "__main__":
    ROOT_DIR = Path(__file__).resolve().parent.parent
    raw_file = ROOT_DIR / "data" / "raw" / "online_retail_II.csv"
    parquet_file = ROOT_DIR / "data" / "raw" / "online_retail_II.parquet"

    if not raw_file.exists():
        print(f"Error: raw file not found at {raw_file}")
        sys.exit(1)

    df = load_raw_data(raw_file)
    validate_dataframe(df)
    save_parquet(df, parquet_file)

    print("Extraction complete.")