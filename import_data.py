import polars as pl

df = pl.read_ndjson("health_data.json")

print("First 5 rows:")
print(df.head(5))
print()

print("Schema:")
print(df.schema)
print()

print(f"Total rows: {df.height}")
print()

print("Null counts per column:")
nulls = df.null_count()
print(nulls)
