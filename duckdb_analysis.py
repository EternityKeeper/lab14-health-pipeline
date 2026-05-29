import duckdb
import polars as pl
import time

# DuckDB query
start = time.perf_counter()
con = duckdb.connect()
result_duck = con.execute("""
    SELECT
        CASE
            WHEN systolic_bp < 120 THEN 'normal'
            WHEN systolic_bp < 130 THEN 'elevated'
            WHEN systolic_bp < 140 THEN 'high_stage1'
            ELSE 'high_stage2'
        END AS bp_group,
        AVG(heart_rate) AS avg_heart_rate,
        MIN(temperature) AS min_temperature,
        COUNT(*) AS record_count
    FROM 'cleaned_health.parquet'
    WHERE spo2 > 96
    GROUP BY bp_group
    ORDER BY bp_group
""").fetchdf()
end_duck = time.perf_counter()
duck_time = end_duck - start

print("DuckDB result (spo2 > 96, grouped by blood pressure):")
print(result_duck)
print(f"DuckDB query time: {duck_time:.4f}s")
print()

# Polars equivalent
start = time.perf_counter()
df = pl.read_parquet("cleaned_health.parquet")
result_pl = df.filter(pl.col("spo2") > 96).with_columns(
    pl.when(pl.col("systolic_bp") < 120).then(pl.lit("normal"))
    .when(pl.col("systolic_bp") < 130).then(pl.lit("elevated"))
    .when(pl.col("systolic_bp") < 140).then(pl.lit("high_stage1"))
    .otherwise(pl.lit("high_stage2"))
    .alias("bp_group")
).group_by("bp_group").agg([
    pl.col("heart_rate").mean().alias("avg_heart_rate"),
    pl.col("temperature").min().alias("min_temperature"),
    pl.len().alias("record_count"),
]).sort("bp_group")
end_pl = time.perf_counter()
pl_time = end_pl - start

print("Polars equivalent result:")
print(result_pl)
print(f"Polars query time: {pl_time:.4f}s")
print()
print(f"Time comparison: DuckDB {duck_time:.4f}s vs Polars {pl_time:.4f}s")
