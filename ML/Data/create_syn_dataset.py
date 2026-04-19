import random
import pandas as pd

data = []

for _ in range(500):  # generate 500 samples

    # Generate temperature
    temp = round(random.uniform(25, 42), 1) # 1 decimals
    
    # Generate turbidity 
    ntu = round(random.uniform(0, 10), 2) # 2 decimals

    # Generate TDS
    tds = round(random.uniform(30, 1500), 0)  # 0 decimals

    # Label logic (based on your table)
    if tds < 600 and ntu < 5:
        label = "GOOD"
    elif tds < 1000 and ntu < 8:
        label = "NORMAL"
    else:
        label = "BAD"

    data.append([temp, tds, ntu, label])

df = pd.DataFrame(data, columns=["temp", "tds", "ntu", "label"])
df.to_csv("train_syn_water_quality.csv", index=False)
#df.to_csv("test_syn_water_quality.csv", index=False)

print("Dataset created!")