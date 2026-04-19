import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report

# LOAD MODEL + Z-SCORE PARAMS
iso_model = joblib.load("iso_model.pkl")
z_params = joblib.load("zscore_params.pkl")

mean = z_params["mean"]
std = z_params["std"]

# Z-SCORE FUNCTION
def z_score_anomaly(tds, ntu, temp, threshold=2.5):
    values = np.array([tds, ntu, temp])
    z_scores = (values - mean) / std
    return any(abs(z) > threshold for z in z_scores)

# ISOLATION FOREST FUNCTION
def iso_forest_anomaly(tds, ntu, temp):
    pred = iso_model.predict([[tds, ntu, temp]])
    return True if pred[0] == -1 else False

# HYBRID DETECTION
def detect_anomaly(tds, ntu, temp):
    return 1 if (z_score_anomaly(tds, ntu, temp) or 
                 iso_forest_anomaly(tds, ntu, temp)) else 0
    # 1 = Anomaly, 0 = Normal


# LOAD TEST DATA
df = pd.read_csv("../Data/test_syn_water_quality.csv")

# MAP TRUE LABELS
# NORMAL → 0, ANOMALY (or BAD) → 1
def map_label(x):
    if x.upper() in ["GOOD", "NORMAL"]:
        return 0
    else:
        return 1

df["true"] = df["label"].apply(map_label)

# PREDICTIONS
df["pred"] = df.apply(lambda row: detect_anomaly(row["tds"], row["ntu"], row["temp"]), axis=1)

# CONFUSION MATRIX
cm = confusion_matrix(df["true"], df["pred"])

print("Confusion Matrix:")
print(cm)

# CLASSIFICATION REPORT
print("\nClassification Report:")
print(classification_report(df["true"], df["pred"], target_names=["Normal", "Anomaly"]))