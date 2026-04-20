import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib


#  LOAD DATASET
df = pd.read_csv("../Data/train_syn_water_quality.csv")


# FILTER NORMAL DATA
# Use GOOD + NORMAL only
df_filtered = df[df["label"].isin(["GOOD", "NORMAL","BAD"])]

print("Total samples:", len(df))
print("Filtered samples (GOOD + NORMAL + BAD):", len(df_filtered))

# SELECT FEATURES
X = df_filtered[["tds", "ntu", "temp"]].values

# TRAIN ISOLATION FOREST
iso_model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

iso_model.fit(X)

# SAVE MODEL
joblib.dump(iso_model, "iso_model.pkl")
print("Isolation Forest model saved!")

# COMPUTE Z-SCORE BASELINE
mean = np.mean(X, axis=0)
std = np.std(X, axis=0)

zscore_params = {
    "mean": mean,
    "std": std
}

joblib.dump(zscore_params, "zscore_params.pkl")
print("Z-score parameters saved!")

# DONE
print("Training complete!")