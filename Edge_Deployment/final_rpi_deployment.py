import serial
import json
import numpy as np
import joblib
import pandas as pd
from tensorflow.keras.models import load_model

# LOAD MODELS
iso_model = joblib.load("./Models/iso_model.pkl")
z_params = joblib.load("./Models/zscore_params.pkl")
wqi_model = joblib.load("./Models/wqi_rf_model.pkl")
lstm_model = load_model("./Models/lstm_model.keras")
scaler = joblib.load("./Models/lstm_scaler.pkl")

mean = z_params["mean"]
std = z_params["std"]

# CONFIG
SEQ_LEN = 10
buffer = []

# Serial (adjust port)
ser = serial.Serial('/dev/ttyUSB0', 9600)

# ANOMALY DETECTION
def z_score_anomaly(tds, ntu, temp, threshold=2.5):
    values = np.array([tds, ntu, temp])
    z_scores = (values - mean) / std
    return any(abs(z) > threshold for z in z_scores)

def iso_forest_anomaly(tds, ntu, temp):
    return iso_model.predict([[tds, ntu, temp]])[0] == -1

def detect_anomaly(tds, ntu, temp):
    if z_score_anomaly(tds, ntu, temp) or iso_forest_anomaly(tds, ntu, temp):
        return "ANOMALY"
    return "NORMAL"

# WQI PREDICTION
def predict_wqi(tds, ntu, temp):
    df = pd.DataFrame([{
        "tds": tds,
        "ntu": ntu,
        "temp": temp
    }])
    return wqi_model.predict(df)[0]

# FILTER LIFE (LSTM)
def predict_filter_status(tds, ntu, temp):
    global buffer

    buffer.append([tds, ntu, temp])

    if len(buffer) < SEQ_LEN:
        return "COLLECT"

    if len(buffer) > SEQ_LEN:
        buffer.pop(0)

    # Normalize
    scaled = scaler.transform(buffer)
    input_seq = np.array(scaled).reshape(1, SEQ_LEN, 3)

    pred_scaled = lstm_model.predict(input_seq, verbose=0)[0][0]

    # Reverse scaling
    dummy = np.array([[pred_scaled, 0, 0]])
    predicted_tds = scaler.inverse_transform(dummy)[0][0]

    # Decision
    if predicted_tds > 1000:
        return "REPLACE_NOW"
    elif predicted_tds > 700:
        return "REPLACE_SOON"
    else:
        return "HEALTHY"

# MAIN LOOP
print("System Started...")

while True:
    try:
        line = ser.readline().decode().strip()

        # Expect JSON input
        data = json.loads(line)

        t1 = data["t1"]   # normal water temp (used)
        t2 = data["t2"]   # hot water temp (only for display)
        tds = data["tds"]
        ntu = data["ntu"]

    
        # PROCESS
    
        anomaly = detect_anomaly(tds, ntu, t1)
        wqi = predict_wqi(tds, ntu, t1)
        filter_status = predict_filter_status(tds, ntu, t1)

    
        # FINAL DECISION
    
        if anomaly == "ANOMALY":
            final_status = "ANOM"
        elif wqi == "BAD":
            final_status = "SERV"
        else:
            final_status = wqi

    
        # SERIAL OUTPUT FORMAT
    
        # Format: STATUS,WQI,FILTER,T1,T2
        output = f"{final_status},{wqi},{filter_status},{round(t1,1)},{round(t2,1)}\n"

        print(" Sending:", output.strip())

        ser.write(output.encode())

    except Exception as e:
        print("Error:", e)