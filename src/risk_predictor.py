import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "risk_model.pkl")



def train_risk_model(data_path):
    df = pd.read_csv(data_path)

    df['crime_code'] = df['crime_type'].astype('category').cat.codes

    X = df[['latitude', 'longitude', 'hour']]
    y = df['crime_code']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    return model


def load_model():
    return joblib.load(MODEL_PATH)


def predict_risk(latitude, longitude, hour):
    model = load_model()
    input_data = pd.DataFrame([[latitude, longitude, hour]],
                              columns=['latitude', 'longitude', 'hour'])
    prediction = model.predict(input_data)[0]
    return prediction

def patrol_recommendation(risk_level):
    if risk_level == 2:
        return "🚨 High priority patrol required"
    elif risk_level == 1:
        return "👮 Moderate patrol suggested"
    else:
        return "✅ Routine patrol sufficient"


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "crime_data.csv")

    model = train_risk_model(data_path)
    print("Risk model trained and saved successfully.")
