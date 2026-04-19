import pandas as pd
import joblib
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

# LOAD TRAINED MODEL
model = joblib.load("wqi_rf_model.pkl")

# LOAD TEST DATA
df = pd.read_csv("../Data/test_syn_water_quality.csv")

# CHECK COLUMN ORDER
# Your CSV: temp, tds, ntu, label
X = df[["tds", "ntu", "temp"]]   # reorder correctly
y_true = df["label"]

# PREDICTION
y_pred = model.predict(X)

# EVALUATION
accuracy = accuracy_score(y_true, y_pred)
cm = confusion_matrix(y_true, y_pred)
report = classification_report(y_true, y_pred)

print("\n Accuracy:", accuracy)

print("\n Confusion Matrix:")
print(cm)

print("\n Classification Report:")
print(report)