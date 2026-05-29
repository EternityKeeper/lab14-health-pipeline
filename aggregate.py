import polars as pl

df = pl.read_parquet("cleaned_health.parquet")

df = df.with_columns(
    pl.when(pl.col("heart_rate") <= 70).then(pl.lit("low"))
    .when(pl.col("heart_rate") <= 85).then(pl.lit("normal"))
    .otherwise(pl.lit("high"))
    .alias("hr_group")
)

result = df.group_by("hr_group").agg([
    pl.col("spo2").mean().alias("avg_spo2"),
    pl.col("systolic_bp").mean().alias("avg_systolic_bp"),
    pl.col("temperature").max().alias("max_temperature"),
    pl.len().alias("count"),
]).sort("hr_group")

print("Aggregation by heart rate group:")
print(result)
