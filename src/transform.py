"""
transform.py — Data cleaning and feature engineering.

Takes the raw DataFrame from extract.py and applies:
  - Null removal and type coercion
  - Cancellation / negative-quantity filtering
  - Derived columns: TotalPrice, InvoiceMonth
  - RFM (Recency, Frequency, Monetary) customer segmentation
  - Monthly revenue aggregates for trend analysis

Returns cleaned DataFrames ready to be loaded into PostgreSQL.

Implementation added in Phase 3.
"""
