import polars as pl

df = pl.read_ndjson("health_data.json")
initial_rows = df.height
print(f"Initial rows: {initial_rows}")
print()

# Step a: remove duplicate rows
before_dedup = df.height
df = df.unique()
dedup_count = before_dedup - df.height
print(f"Step a: removed {dedup_count} duplicate rows")
print()

# Step b: handle missing values
numeric_cols = ["heart_rate", "systolic_bp", "diastolic_bp", "temperature", "spo2"]
total_cells = df.height * len(df.columns)
null_counts = df.null_count()
total_nulls = sum(null_counts.row(0))
null_pct = total_nulls / total_cells * 100 if total_cells > 0 else 0
print(f"Null percentage: {null_pct:.2f}%")

if null_pct < 5:
    for col in numeric_cols:
        median_val = df[col].median()
        df = df.with_columns(pl.col(col).fill_null(median_val).alias(col))
        nulls_filled = null_counts[col].item()
        if nulls_filled > 0:
            print(f"  Filled {nulls_filled} nulls in '{col}' with median ({median_val})")
    if "timestamp" in df.columns:
        ts_nulls = df["timestamp"].null_count()
        if ts_nulls > 0:
            df = df.with_columns(pl.col("timestamp").forward_fill())
            print(f"  Forward-filled {ts_nulls} nulls in 'timestamp'")
else:
    rows_before = df.height
    df = df.drop_nulls()
    dropped = rows_before - df.height
    print(f"  Nulls >= 5%, dropped {dropped} rows")
print()

# Step c: cast types
df = df.with_columns(
    pl.col("timestamp").str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%z").alias("timestamp"),
    pl.col("heart_rate").cast(pl.Int64),
    pl.col("systolic_bp").cast(pl.Int64),
    pl.col("diastolic_bp").cast(pl.Int64),
    pl.col("temperature").cast(pl.Float64),
    pl.col("spo2").cast(pl.Int64),
)
print("Step c: types cast (timestamp -> datetime, numerics -> int/float)")
print()

# Final stats
print(f"Final row count: {df.height}")
print(f"Nulls after cleaning:")
print(df.null_count())
print()

print("Numeric columns statistics (mean, min, max):")
stats = df.select(
    [pl.col(c).mean().alias(f"{c}_mean") for c in numeric_cols]
    + [pl.col(c).min().alias(f"{c}_min") for c in numeric_cols]
    + [pl.col(c).max().alias(f"{c}_max") for c in numeric_cols]
)
print(stats)
