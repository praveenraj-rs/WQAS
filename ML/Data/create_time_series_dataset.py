import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# CONFIGURATION
TOTAL_POINTS = 1000          # total samples
CYCLE_LENGTH = 200           # points before filter replacement
START_TIME = datetime(2026, 1, 1, 0, 0, 0)

data = []

current_time = START_TIME

# GENERATE DATA
for i in range(TOTAL_POINTS):

    # Simulate filter cycles
    cycle_position = i % CYCLE_LENGTH

    # --------------------------
    # TDS (increases over time)
    # --------------------------
    tds_base = 200 + (cycle_position * 4)   # increasing trend

    tds_noise = np.random.normal(0, 15)     # sensor noise
    tds = tds_base + tds_noise

    # --------------------------
    # Turbidity (slight increase)
    # --------------------------
    ntu_base = 5 + (cycle_position * 0.05)

    ntu_noise = np.random.normal(0, 1)
    ntu = ntu_base + ntu_noise

    # --------------------------
    # Temperature (slow variation)
    # --------------------------
    temp = 25 + 5 * np.sin(i / 50) + np.random.normal(0, 0.5)

    # --------------------------
    # Append data
    # --------------------------
    data.append([
        current_time,
        round(tds, 2),
        round(ntu, 2),
        round(temp, 2)
    ])

    # Increment time (1 minute interval)
    current_time += timedelta(minutes=1)


# CREATE DATAFRAME
df = pd.DataFrame(data, columns=["timestamp", "tds", "ntu", "temp"])

# SAVE CSV
df.to_csv("time_series_data.csv", index=False)

print("Time-series dataset generated: time_series_data.csv")