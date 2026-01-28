import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "risk_model.pkl")


# ---------------- TRAIN MODEL ----------------
def train_risk_model(data_path):
    df = pd.read_csv(data_path)

    # Convert crime types to categorical codes
    df['crime_type'] = df['crime_type'].astype('category')
    df['crime_code'] = df['crime_type'].cat.codes

    # Save mapping of code -> crime name
    crime_mapping = dict(enumerate(df['crime_type'].cat.categories))

    X = df[['latitude', 'longitude', 'hour']]
    y = df['crime_code']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump((model, crime_mapping), MODEL_PATH)
    print("Risk model trained and saved successfully.")


# ---------------- LOAD MODEL ----------------
def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Risk model not found. Train it first.")
    model, crime_mapping = joblib.load(MODEL_PATH)
    return model, crime_mapping


# ---------------- PREDICT RISK ----------------
def predict_risk(latitude, longitude, hour):
    model, crime_mapping = load_model()

    input_data = pd.DataFrame([[latitude, longitude, hour]],
                              columns=['latitude', 'longitude', 'hour'])

    crime_code = model.predict(input_data)[0]
    crime_type = crime_mapping[crime_code]

    # Define risk levels based on crime severity
    high_risk = ["Robbery", "Assault", "Burglary"]
    medium_risk = ["Theft", "Accident"]

    if crime_type in high_risk:
        return 2  # High Risk
    elif crime_type in medium_risk:
        return 1  # Medium Risk
    else:
        return 0  # Low Risk


# ---------------- PATROL RECOMMENDATION ----------------
def patrol_recommendation(risk_level):
    risk_level = int(risk_level)

    if risk_level == 2:
        return "🚨 High patrol frequency needed"
    elif risk_level == 1:
        return "👮 Moderate patrol suggested"
    else:
        return "✅ Routine patrol sufficient"


# ---------------- RUN TRAINING IF CALLED DIRECTLY ----------------
if __name__ == "__main__":
    data_file = os.path.join(os.path.dirname(__file__), "..", "data", "crime_data.csv")
    train_risk_model(data_file)
