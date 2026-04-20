"""
Flask Dashboard Backend — Water Dispenser AI Monitor
Receives serial data from Arduino, runs ML inference, serves dashboard.
"""

import serial
import json
import threading
import time
import numpy as np
from flask import Flask, render_template, jsonify
from collections import deque
from datetime import datetime

app = Flask(__name__)

# CONFIG
SERIAL_PORT = '/dev/ttyACM1'
BAUD_RATE = 9600
SEQ_LEN = 10
MOCK_MODE = False  # Set False when hardware connected
MOCK_STATE = "NORMAL" # GOOD, NORMAL, BAD, ANOMALY

# GLOBAL STATE
latest_data = {
    "t1": None, "t2": None,
    "tds": None, "ntu": None,
    "anomaly": "–", "wqi": "–",
    "filter_status": "–", "final_status": "–",
    "timestamp": None,
    "wqi_score": None
}

history = deque(maxlen=30)  # Last 30 readings for charts
buffer = []  # LSTM sequence buffer

# LOAD MODELS (wrapped so dashboard works even without model files)
models_loaded = True
iso_model = z_mean = z_std = wqi_model = lstm_model = scaler = None

try:
    import joblib
    from tensorflow.keras.models import load_model
    import pandas as pd

    iso_model   = joblib.load("./Models/iso_model.pkl")
    z_params    = joblib.load("./Models/zscore_params.pkl")
    wqi_model   = joblib.load("./Models/wqi_rf_model.pkl")
    lstm_model  = load_model("./Models/lstm_model.keras")
    scaler      = joblib.load("./Models/lstm_scaler.pkl")

    z_mean = z_params["mean"]
    z_std  = z_params["std"]
    models_loaded = True
    print("✅ All models loaded.")
except Exception as e:
    print(f"⚠️  Model loading skipped ({e}). Running in MOCK mode.")
    MOCK_MODE = True

# ML INFERENCE FUNCTIONS

def z_score_anomaly(tds, ntu, temp, threshold=2.5):
    values = np.array([tds, ntu, temp])
    z = (values - z_mean) / z_std
    return bool(any(abs(zi) > threshold for zi in z))

def iso_forest_anomaly(tds, ntu, temp):
    return iso_model.predict([[tds, ntu, temp]])[0] == -1

def detect_anomaly(tds, ntu, temp):
    if not models_loaded:
        return "NORMAL"
    if z_score_anomaly(tds, ntu, temp) or iso_forest_anomaly(tds, ntu, temp):
        return "ANOMALY"
    return "NORMAL"

def predict_wqi(tds, ntu, temp):
    """Returns (label, score). Score is 0–100 for gauge."""
    if not models_loaded:
        # Mock score based on TDS
        score = max(0, min(100, 100 - (tds / 15)))
        label = "EXCELLENT" if score > 80 else "GOOD" if score > 60 else "FAIR" if score > 40 else "BAD"
        return label, round(score, 1)
    
    import pandas as pd
    df = pd.DataFrame([{"tds": tds, "ntu": ntu, "temp": temp}])
    # If model returns a label directly:
    label = wqi_model.predict(df)[0]
    # Derive a numeric score for display (customize if your model outputs probabilities)
    score_map = {"GOOD": 80, "FAIR": 45, "BAD": 20}
    score = score_map.get(str(label).upper(), 50)
    return str(label).upper(), score

def predict_filter_status(tds, ntu, temp):
    global buffer
    buffer.append([tds, ntu, temp])
    if len(buffer) > SEQ_LEN:
        buffer.pop(0)
    if len(buffer) < SEQ_LEN:
        return "COLLECTING", len(buffer)

    if not models_loaded:
        pred_tds = tds * 1.05  # Mock: slight degradation
    else:
        scaled = scaler.transform(buffer)
        inp = np.array(scaled).reshape(1, SEQ_LEN, 3)
        pred_scaled = lstm_model.predict(inp, verbose=0)[0][0]
        dummy = np.array([[pred_scaled, 0, 0]])
        pred_tds = scaler.inverse_transform(dummy)[0][0]

    pct = max(0, min(100, 100 - ((pred_tds - 200) / 10)))  # 200=clean, 1200=replace

    if pred_tds > 1000:
        return "REPLACE NOW", round(pct)
    elif pred_tds > 700:
        return "REPLACE SOON", round(pct)
    else:
        return "HEALTHY", round(pct)

# PROCESS ONE SENSOR READING

def process_reading(t1, t2, tds, ntu):
    global latest_data

    anomaly = detect_anomaly(tds, ntu, t1)
    wqi_label, wqi_score = predict_wqi(tds, ntu, t1)
    filter_result = predict_filter_status(tds, ntu, t1)

    if isinstance(filter_result, tuple):
        filter_status, filter_pct = filter_result
    else:
        filter_status, filter_pct = filter_result, 0

    if anomaly == "ANOMALY":
        final_status = "ANOMALY"
    elif wqi_label == "BAD":
        final_status = "SERVICE NEEDED"
    else:
        final_status = wqi_label

    reading = {
        "t1": round(t1, 1), "t2": round(t2, 1),
        "tds": round(tds, 1), "ntu": round(ntu, 2),
        "anomaly": anomaly,
        "wqi": wqi_label, "wqi_score": wqi_score,
        "filter_status": filter_status, "filter_pct": filter_pct,
        "final_status": final_status,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }

    latest_data = reading
    history.append({
        "time": reading["timestamp"],
        "tds": reading["tds"],
        "ntu": reading["ntu"],
        "t1": reading["t1"],
        "wqi_score": wqi_score
    })

    print(f"📊 {reading['timestamp']} | TDS:{tds} NTU:{ntu} T1:{t1}°C | {final_status}")

# MOCK DATA GENERATOR (for testing without hardware)

def mock_serial_loop():
    """Generates realistic sensor data for UI testing."""
    t = 0
# Good
    if (MOCK_STATE =="GOOD"):
        while True:
            t += 1
            t1  = 28.5 + np.random.normal(0, 0.3)
            t2  = 65.0 + np.random.normal(0, 0.5)
            tds = 320 + 15 * np.sin(t / 10) + np.random.normal(0, 10)
            ntu = 2 + 2 * np.sin(t / 8) + np.random.normal(0, 0.5)

            # Inject occasional anomaly spike
            if t % 47 == 0:
                tds += 800

            process_reading(t1, t2, max(0, tds), max(0, ntu))
            time.sleep(5)

# Normal
    elif (MOCK_STATE =="NORMAL"):
        while True:
            t += 1
            t1  = 28.5 + np.random.normal(0, 0.3)
            t2  = 65.0 + np.random.normal(0, 0.5)
            tds = 600 + 15 * np.sin(t / 10) + np.random.normal(0, 10)
            ntu = 5 + 2 * np.sin(t / 8) + np.random.normal(0, 0.5)

            # Inject occasional anomaly spike
            if t % 47 == 0:
                tds += 800

            process_reading(t1, t2, max(0, tds), max(0, ntu))
            time.sleep(5)

# Bad
    elif (MOCK_STATE =="BAD"):
        while True:
            t += 1
            t1  = 28.5 + np.random.normal(0, 0.3)
            t2  = 65.0 + np.random.normal(0, 0.5)
            tds = 950 + 15 * np.sin(t / 10) + np.random.normal(0, 10)
            ntu = 7 + 2 * np.sin(t / 8) + np.random.normal(0, 0.5)

            # Inject occasional anomaly spike
            if t % 47 == 0:
                tds += 800

            process_reading(t1, t2, max(0, tds), max(0, ntu))
            time.sleep(5)

# Anomaly
    elif (MOCK_STATE =="ANOMALY"):
        while True:
            t += 1
            t1  = 28.5 + np.random.normal(0, 20)
            t2  = 65.0 + np.random.normal(0, 0.5)
            tds = 950 + 50 * np.sin(t / 10) + np.random.normal(0, 10)
            ntu = 7 + 10 * np.sin(t / 8) + np.random.normal(0, 0.5)

            # Inject occasional anomaly spike
            if t % 47 == 0:
                tds += 800

            process_reading(t1, t2, max(0, tds), max(0, ntu))
            time.sleep(5)
# REAL SERIAL READER

# def serial_loop():
#     while True:
#         try:
#             ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
#             print(f"✅ Serial connected: {SERIAL_PORT}")
#             while True:
#                 line = ser.readline().decode().strip()
#                 if not line:
#                     continue
#                 data = json.loads(line)
#                 process_reading(
#                     data["t1"], data["t2"],
#                     data["tds"], data["ntu"]
#                 )
#         except Exception as e:
#             print(f" Serial error: {e}. Retrying in 5s...")
#             time.sleep(5)


def serial_loop():
    while True:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
            print(f"✅ Serial connected: {SERIAL_PORT}")

            while True:
                line = ser.readline().decode().strip()
                if not line:
                    continue

                data = json.loads(line)

                # Process data
                process_reading(
                    data["t1"], data["t2"],
                    data["tds"], data["ntu"]
                )

                # ✅ SEND WQI BACK TO ARDUINO
                wqi_to_send = latest_data["wqi"]  # EXCELLENT / GOOD / BAD etc.
                ser.write((wqi_to_send + "\n").encode())

                print(f"➡️ Sent to Arduino: {wqi_to_send}")

        except Exception as e:
            print(f" Serial error: {e}. Retrying in 5s...")
            time.sleep(5)

# FLASK ROUTES

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/latest')
def api_latest():
    return jsonify(latest_data)

@app.route('/api/history')
def api_history():
    return jsonify(list(history))

@app.route('/api/status')
def api_status():
    return jsonify({
        "models_loaded": models_loaded,
        "mock_mode": MOCK_MODE,
        "buffer_fill": len(buffer),
        "seq_len": SEQ_LEN
    })

# STARTUP

if __name__ == '__main__':
    target = mock_serial_loop if MOCK_MODE else serial_loop
    t = threading.Thread(target=target, daemon=True)
    t.start()
    print(f"Dashboard: http://localhost:5000  |  Mock: {MOCK_MODE}")
    app.run(host='0.0.0.0', port=5000, debug=False)
