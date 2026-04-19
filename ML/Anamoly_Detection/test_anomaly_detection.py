import joblib
import numpy as np
import json

# LOAD MODEL + Z-SCORE PARAMS
iso_model = joblib.load("iso_model.pkl")
z_params = joblib.load("zscore_params.pkl")

mean = z_params["mean"]
std = z_params["std"]

# Z-SCORE FUNCTION
def z_score_anomaly(tds, ntu, temp, threshold=2.5):

    values = np.array([tds, ntu, temp])

    z_scores = (values - mean) / std

    # Check each feature
    if any(abs(z) > threshold for z in z_scores):
        return True
    return False


# ISOLATION FOREST FUNCTION
def iso_forest_anomaly(tds, ntu, temp):

    pred = iso_model.predict([[tds, ntu, temp]])

    # -1 → anomaly
    return True if pred[0] == -1 else False


# HYBRID DETECTION
def detect_anomaly(tds, ntu, temp):

    z_flag = z_score_anomaly(tds, ntu, temp)
    iso_flag = iso_forest_anomaly(tds, ntu, temp)

    if z_flag or iso_flag:
        return "ANOMALY"
    else:
        return "NORMAL"


# TEST INPUT (SIMULATION)
if __name__ == "__main__":

    # Example test data
    test_data = [
        {"tds": 250, "ntu": 5, "temp": 27},   # normal
        {"tds": 1200, "ntu": 50, "temp": 40}, # anomaly
    ]

    for data in test_data:
        result = detect_anomaly(data["tds"], data["ntu"], data["temp"])
        print(data, "→", result)