import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

# LOAD TEST DATA
df = pd.read_csv("../Data/test_syn_water_quality.csv")

# MAP TRUE LABELS
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

# NORMALIZE (for percentage display)
cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

# LABELS
labels = ["Normal", "Anomaly"]

# CREATE ANNOTATION (count + %)
annot = np.empty_like(cm).astype(str)
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        annot[i, j] = f"{cm[i, j]}\n({cm_percent[i, j]:.1f}%)"

# PLOT
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=annot, fmt="", cmap="Blues",
            xticklabels=labels, yticklabels=labels)

plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title("Confusion Matrix")
plt.tight_layout()

# SAVE FIGURE (for report)
plt.savefig("confusion_matrix.png", dpi=300)

plt.show()

# PRINT TEXT REPORT
print("\nConfusion Matrix:")
print(cm)

print("\nClassification Report:")
print(classification_report(df["true"], df["pred"], target_names=labels))