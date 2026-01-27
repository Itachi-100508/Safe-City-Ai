import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from src.hotspot_model import find_hotspots
from src.risk_predictor import predict_risk, patrol_recommendation
import os

# ---------------- Page Setup ----------------
st.set_page_config(page_title="SafeCity Crime Map", layout="wide")
st.title("🚔 SafeCity – Smart Crime Mapping & Predictive Policing")

# ---------------- Load Data ----------------
base_dir = os.getcwd()
data_path = os.path.join(base_dir, "data", "crime_data.csv")

try:
    df, _ = find_hotspots(data_path)
except Exception as e:
    st.error("❌ Failed to load hotspot model")
    st.exception(e)
    st.stop()

df["hour"] = df["hour"].astype(int)

# ---------------- Sidebar: Crime Risk Prediction ----------------
st.sidebar.header("🔮 Crime Risk Prediction")

latitude = st.sidebar.number_input(
    "Enter Latitude", value=float(df["latitude"].mean())
)
longitude = st.sidebar.number_input(
    "Enter Longitude", value=float(df["longitude"].mean())
)
hour = st.sidebar.slider("Select Hour of Day", 0, 23, 20)

if st.sidebar.button("Predict Crime Risk"):
    prediction = predict_risk(latitude, longitude, hour)
    risk_labels = {
        0: "Low Risk 🟢",
        1: "Medium Risk 🟡",
        2: "High Risk 🔴"
    }
    st.sidebar.success(
        f"Predicted Risk Level: {risk_labels.get(prediction, 'Unknown')}"
    )
    recommendation = patrol_recommendation(prediction)
    st.sidebar.info(f"Patrol Recommendation: {recommendation}")

# ---------------- Predictive Logic ----------------
def night_crime_ratio(df, cluster_id):
    cluster_data = df[df["cluster"] == cluster_id]
    night_crimes = cluster_data[
        (cluster_data["hour"] >= 20) | (cluster_data["hour"] <= 5)
    ]
    return len(night_crimes) / max(len(cluster_data), 1)

def classify_risk(ratio):
    if ratio > 0.6:
        return "RED"
    elif ratio > 0.35:
        return "YELLOW"
    else:
        return "GREEN"

def hotspot_recommendation(risk):
    if risk == "RED":
        return "HIGH - 3 patrols/hour"
    elif risk == "YELLOW":
        return "MEDIUM - 1-2 patrols/hour"
    else:
        return "LOW - Passive monitoring"

# ---------------- Explanation Panel ----------------
st.markdown("""
### 🧠 Predictive Crime Intelligence (Time-based)

🟥 **Red Zone** → High night-time crime concentration  
🟨 **Yellow Zone** → Mixed crime pattern  
🟩 **Green Zone** → Mostly daytime / low-risk  

🚓 Patrols are **AI-recommended** based on exposure level.
""")

# ---------------- Create Map ----------------
map_center = [df["latitude"].mean(), df["longitude"].mean()]
crime_map = folium.Map(location=map_center, zoom_start=12)

# ---------------- Crime Markers ----------------
marker_cluster = MarkerCluster().add_to(crime_map)
for _, row in df.iterrows():
    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=f"""
        <b>Crime ID:</b> {row['crime_id']}<br>
        <b>Type:</b> {row['crime_type']}<br>
        <b>Hour:</b> {row['hour']}:00
        """,
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(marker_cluster)

# ---------------- Predictive Hotspots (ATTRACTIVE POPUP) ----------------
for cluster_id in df["cluster"].unique():
    cluster_df = df[df["cluster"] == cluster_id]
    center = [
        cluster_df["latitude"].mean(),
        cluster_df["longitude"].mean(),
    ]

    ratio = night_crime_ratio(df, cluster_id)
    risk = classify_risk(ratio)
    patrol = hotspot_recommendation(risk)

    color_map = {
        "RED": "#dc2626",
        "YELLOW": "#f59e0b",
        "GREEN": "#16a34a"
    }

    folium.Circle(
        location=center,
        radius=700,
        color=risk.lower(),
        fill=True,
        fill_opacity=0.45,
        popup=f"""
        <div style="
            font-family: Arial, sans-serif;
            padding: 14px;
            width: 230px;
            border-radius: 14px;
            background: linear-gradient(135deg,#111827,#1f2933);
            color: white;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        ">
            <div style="font-weight:700;font-size:15px;margin-bottom:8px;">
                🔮 Predictive Hotspot
            </div>

            <div style="
                display:inline-block;
                padding:5px 12px;
                border-radius:999px;
                font-size:12px;
                font-weight:700;
                margin-bottom:10px;
                background:{color_map[risk]};
            ">
                {risk} RISK
            </div>

            <div style="font-size:13px;">
                🌙 <b>Night Crime Ratio</b>
                <div style="
                    margin-top:4px;
                    font-size:22px;
                    font-weight:800;
                ">
                    {round(ratio, 2)}
                </div>
            </div>

            <hr style="border:none;height:1px;background:rgba(255,255,255,0.15);margin:10px 0;">

            <div style="font-size:13px;">
                🚓 <b>Patrol Recommendation</b>
                <div style="margin-top:6px;font-weight:700;color:#fca5a5;">
                    {patrol}
                </div>
            </div>

            <div style="margin-top:10px;font-size:11px;opacity:0.7;">
                AI-generated operational insight
            </div>
        </div>
        """
    ).add_to(crime_map)

# ---------------- Display ----------------
st.subheader("📍 Crime Incidents & AI-Predicted Risk Zones")
st.components.v1.html(crime_map._repr_html_(), height=600)