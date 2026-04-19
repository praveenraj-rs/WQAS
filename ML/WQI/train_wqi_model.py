import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# LOAD DATA
df = pd.read_csv("../Data/train_syn_water_quality.csv")

# FEATURES & LABEL
X = df[["tds", "ntu", "temp"]]
y = df["label"]

# TRAIN-TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# TRAIN RANDOM FOREST
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)

# TEST MODEL
y_pred = model.predict(X_test)

# EVALUATION
accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy:", accuracy)
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# SAVE MODEL
joblib.dump(model, "wqi_rf_model.pkl")
print("\nModel saved as wqi_rf_model.pkl")