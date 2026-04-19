import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

# LOAD MODEL
model = joblib.load("wqi_rf_model.pkl")

# LOAD DATA
df = pd.read_csv("../Data/test_syn_water_quality.csv")

# FEATURES (correct order)
X = df[["tds", "ntu", "temp"]]
y_true = df["label"]

# PREDICT
y_pred = model.predict(X)

# METRICS
accuracy = accuracy_score(y_true, y_pred)
cm = confusion_matrix(y_true, y_pred)

labels = ["BAD", "GOOD", "NORMAL"]

# NORMALIZE FOR %
cm_percent = cm.astype(float) / cm.sum(axis=1)[:, np.newaxis] * 100

# CREATE ANNOTATION (count + %)
annot = np.empty_like(cm).astype(str)
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        annot[i, j] = f"{cm[i, j]}\n({cm_percent[i, j]:.1f}%)"

# PLOT
plt.figure(figsize=(7, 6))
sns.heatmap(cm,
            annot=annot,
            fmt="",
            cmap="Blues",
            xticklabels=labels,
            yticklabels=labels,
            cbar=True)

plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title(f"Confusion Matrix (Accuracy = {accuracy:.3f})")
plt.tight_layout()

# SAVE FOR REPORT
plt.savefig("confusion_matrix_multiclass.png", dpi=300)

plt.show()

# TEXT OUTPUT
print("\nAccuracy:", accuracy)

print("\nConfusion Matrix:")
print(cm)

print("\nClassification Report:")
print(classification_report(y_true, y_pred))


