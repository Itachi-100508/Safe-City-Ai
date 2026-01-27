import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import os
import joblib

def train_risk_model(data_path):
    df = pd.read_csv(data_path)

    # Encode crime type
    df['crime_code'] = df['crime_type'].astype('category').cat.codes

    X = df[['latitude', 'longitude', 'hour']]
    y = df['crime_code']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    return model

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "crime_data.csv")

    model = train_risk_model(data_path)
    print("Risk prediction model trained successfully.")
