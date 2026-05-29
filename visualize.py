import polars as pl
import matplotlib.pyplot as plt

df = pl.read_parquet("cleaned_health.parquet")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Plot 1: Heart rate and SpO2 over time
times = df["timestamp"].to_list()
hr = df["heart_rate"].to_list()
spo2 = df["spo2"].to_list()

ax1.plot(times, hr, label="Heart Rate (bpm)", color="red", alpha=0.7)
ax1.set_ylabel("Heart Rate (bpm)")
ax1.set_title("Heart Rate and SpO2 Over Time")
ax1.legend(loc="upper left")
ax1.tick_params(axis="x", rotation=45)

ax1b = ax1.twinx()
ax1b.plot(times, spo2, label="SpO2 (%)", color="blue", alpha=0.7)
ax1b.set_ylabel("SpO2 (%)")
ax1b.legend(loc="upper right")

# Plot 2: Temperature histogram
temps = df["temperature"].to_list()
ax2.hist(temps, bins=20, color="green", alpha=0.7, edgecolor="black")
ax2.set_xlabel("Temperature (°C)")
ax2.set_ylabel("Frequency")
ax2.set_title("Temperature Distribution")

plt.tight_layout()
plt.savefig("heart_rate_spo2_timeseries.png")
plt.savefig("temperature_histogram.png")
plt.close()

print("Saved plots: heart_rate_spo2_timeseries.png, temperature_histogram.png")
