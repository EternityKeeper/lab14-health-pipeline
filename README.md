Сурков Всеволод Сергеевич, группа 220032-11, вариант 22, лабораторная 14, сложность средняя
# Lab 14: Health Data Processing Pipeline

## Architecture

```
Go collector (main.go) → health_data.json → Python processing pipeline
                                              ├── import_data.py (preview)
                                              ├── clean_data.py (cleaning & stats)
                                              ├── save_parquet.py (save as Parquet)
                                              ├── aggregate.py (group analysis)
                                              ├── duckdb_analysis.py (SQL vs Polars)
                                              └── visualize.py (plots)
```

## Dependencies

- **Go**: standard library only (no external packages)
- **Python**: polars, duckdb, matplotlib (see `requirements.txt`)

## How to Run

Execute in this order:

```bash
# 1. Generate health data (run for a few seconds, then Ctrl+C)
go run main.go

# 2. Preview raw data
python import_data.py

# 3. Clean data and display statistics
python clean_data.py

# 4. Clean and save as Parquet
python save_parquet.py

# 5. Aggregate analysis from Parquet
python aggregate.py

# 6. SQL analysis with DuckDB vs Polars
python duckdb_analysis.py

# 7. Generate visualizations
python visualize.py
```

## Expected Output (Brief)

### import_data.py
```
First 5 rows: (table with timestamp, heart_rate, systolic_bp, ...)
Schema: {columns with dtypes}
Total rows: N
Null counts: (zeros initially)
```

### clean_data.py
```
Initial rows: N
Step a: removed 0 duplicate rows
Null percentage: 0.00%
Step c: types cast
Final row count: N
Numeric statistics: mean, min, max for each column
```

### save_parquet.py
```
Saved cleaned data to cleaned_health.parquet
JSON file size: X bytes
Parquet file size: Y bytes
Parquet is Z.x times smaller than JSON
```

### aggregate.py
```
Aggregation by heart rate group: (table with avg_spo2, avg_systolic_bp, max_temp, count)
```

### duckdb_analysis.py
```
DuckDB result: (table grouped by bp_group)
DuckDB query time: X.XXXXs
Polars result: (equivalent table)
Polars query time: Y.YYYYs
Time comparison: ...
```

### visualize.py
```
Saved plots: heart_rate_spo2_timeseries.png, temperature_histogram.png
```

## Notes

- `main.go` must be run first to generate `health_data.json` — the rest depends on it.
- `save_parquet.py` must run before `aggregate.py`, `duckdb_analysis.py`, and `visualize.py` since they read from `cleaned_health.parquet`.
- `import_data.py` and `clean_data.py` work directly with the JSON file and can run before `save_parquet.py`.
