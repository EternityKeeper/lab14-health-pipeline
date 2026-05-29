import polars as pl
import os

df = pl.read_ndjson("health_data.json")

df = df.unique()

numeric_cols = ["heart_rate", "systolic_bp", "diastolic_bp", "temperature", "spo2"]
total_nulls = sum(df.null_count().row(0))
total_cells = df.height * len(df.columns)
null_pct = total_nulls / total_cells * 100 if total_cells > 0 else 0

if null_pct < 5:
    for col in numeric_cols:
        median_val = df[col].median()
        df = df.with_columns(pl.col(col).fill_null(median_val))
    if "timestamp" in df.columns:
        df = df.with_columns(pl.col("timestamp").forward_fill())
else:
    df = df.drop_nulls()

df = df.with_columns(
    pl.col("timestamp").str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%z").alias("timestamp"),
    pl.col("heart_rate").cast(pl.Int64),
    pl.col("systolic_bp").cast(pl.Int64),
    pl.col("diastolic_bp").cast(pl.Int64),
    pl.col("temperature").cast(pl.Float64),
    pl.col("spo2").cast(pl.Int64),
)

df.write_parquet("cleaned_health.parquet")

json_size = os.path.getsize("health_data.json")
parquet_size = os.path.getsize("cleaned_health.parquet")

print(f"Saved cleaned data to cleaned_health.parquet")
print(f"JSON file size:   {json_size:,} bytes")
print(f"Parquet file size: {parquet_size:,} bytes")
print(f"Parquet is {json_size / parquet_size:.1f}x smaller than JSON")
