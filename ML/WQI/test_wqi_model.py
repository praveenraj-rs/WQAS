import joblib
import pandas as pd

# LOAD MODEL
wqi_model = joblib.load("wqi_rf_model.pkl")

def predict_wqi(tds, ntu, temp):

    # Use DataFrame with correct column names
    input_df = pd.DataFrame([{
        "tds": tds,
        "ntu": ntu,
        "temp": temp
    }])

    prediction = wqi_model.predict(input_df)
    return prediction[0]


if __name__ == "__main__":

    test_data = [
        {"tds": 250, "ntu": 3, "temp": 25},
        {"tds": 500, "ntu": 10, "temp": 30},
        {"tds": 1200, "ntu": 40, "temp": 35},

        {"tds": 2000, "ntu": 3, "temp": 35},
        {"tds": 650, "ntu": 6, "temp": 35},
        {"tds": 400, "ntu": 4, "temp": 55},
    ]

    for data in test_data:
        result = predict_wqi(data["tds"], data["ntu"], data["temp"])
        print(data, "→", result)