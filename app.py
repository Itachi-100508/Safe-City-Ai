import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from src.hotspot_model import find_hotspots
from src.risk_predictor import predict_risk, patrol_recommendation
import os

# ---------------- PAGE CONFIG (MUST BE FIRST STREAMLIT CALL) ----------------
st.set_page_config(page_title="SafeCity Crime Map", layout="wide")

# ---------------- GLOBAL STYLES ----------------
st.markdown("""
<style>

/* Remove default spacing & scrolling */
html, body, [data-testid="stAppViewContainer"], .stApp {
    height: 100vh;
    overflow: hidden !important;
}

section[data-testid="stSidebar"] {
    height: 100vh;
    overflow: hidden !important;
}

.block-container {
    padding: 0rem;
    height: 100vh;
    overflow: hidden;
}


.block-container {
    padding: 0rem;
}

/* Style the native Streamlit header bar */
header[data-testid="stHeader"] {
    background-color: #1f2937 !important;
    border-bottom: 2px solid #374151;
}

/* Add custom title in the header */
header[data-testid="stHeader"]::before {
    content: "🚔 SafeCity - Smart Crime Mapping & Predictive App";
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    color: white;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.5px;
    line-height: 50px;
    z-index: 1000;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #000000 !important;
    padding: 15px;
    border-right: 1px solid #1f2937;
}


/* Sidebar header */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white !important;
}

/* Sidebar footer text */
.sidebar-footer {
    position: absolute;
    bottom: 20px;
    width: 100%;
    text-align: center;
    color: #9ca3af;
    font-size: 13px;
}
            
/* Sidebar labels and text */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: #e5e7eb !important;
}

/* Sidebar text colors for specific elements */
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #d1d5db !important;
}

/* Sidebar input fields */
section[data-testid="stSidebar"] input {
    background-color: white !important;
    color: #1f2937 !important;
    border: 1px solid #d1d5db !important;
}

/* Remove sidebar internal scrolling */
section[data-testid="stSidebar"] > div:first-child {
    height: 100vh !important;
    overflow: hidden !important;
}

/* Fix the +/- increment buttons - STRONGER SELECTORS */
section[data-testid="stSidebar"] div[data-baseweb="input"] button,
section[data-testid="stSidebar"] button[kind="stepperButton"],
section[data-testid="stSidebar"] [data-testid="stNumberInput"] button {
    background-color: #10b981 !important;
    color: white !important;
    min-width: 40px !important;
}

section[data-testid="stSidebar"] div[data-baseweb="input"] button:hover,
section[data-testid="stSidebar"] button[kind="stepperButton"]:hover,
section[data-testid="stSidebar"] [data-testid="stNumberInput"] button:hover {
    background-color: #059669 !important;
}

section[data-testid="stSidebar"] div[data-baseweb="input"] button svg,
section[data-testid="stSidebar"] button[kind="stepperButton"] svg,
section[data-testid="stSidebar"] [data-testid="stNumberInput"] button svg {
    fill: white !important;
    color: white !important;
}

/* Main action button - Predict Crime Risk */
section[data-testid="stSidebar"] .stButton button {
    background-color: #ef4444 !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 16px !important;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background-color: #dc2626 !important;
}

section[data-testid="stSidebar"] button[kind="primary"]:hover,
section[data-testid="stSidebar"] button[kind="primaryFormSubmit"]:hover {
    background-color: #b91c1c !important;
}

/* All other sidebar buttons (fallback) */
section[data-testid="stSidebar"] button {
    color: white !important;
}

/* Map legend */
.map-legend {
    position: absolute;
    bottom: 25px;
    right: 25px;
    z-index: 999;
    background-color: rgba(0,0,0,0.85);
    padding: 14px 18px;
    border-radius: 10px;
    color: white;
    font-size: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="sidebar-footer">
        Team – Neural Navigators ~ VSIT
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown("""
<div class="map-legend">
<b>Map Legend</b><br><br>
🟥 Red Zone → High night-time crime concentration<br>
🟨 Yellow Zone → Mixed crime pattern<br>
🟩 Green Zone → Mostly daytime / low-risk
</div>
""", unsafe_allow_html=True)


# Use the correct path structure with data/ folder
data_path = os.path.join("data", "crime_data.csv")

try:
    df, _ = find_hotspots(data_path)
except Exception as e:
    st.error("❌ Failed to load hotspot model")
    st.exception(e)
    st.stop()

df["hour"] = df["hour"].astype(int)

# ---------------- SIDEBAR CONTROLS ----------------
st.sidebar.header("🔮 Crime Risk Prediction")

latitude = st.sidebar.number_input(
    "Enter Latitude",
    value=float(df["latitude"].mean()),
    format="%.4f",
    step=0.0001
)

longitude = st.sidebar.number_input(
    "Enter Longitude",
    value=float(df["longitude"].mean()),
    format="%.4f",
    step=0.0001
)

hour = st.sidebar.slider("Select Hour of Day", 0, 23, 20)

if st.sidebar.button("Predict Crime Risk"):
    prediction = predict_risk(latitude, longitude, hour)
    risk_labels = {
        0: "Low Risk 🟢",
        1: "Medium Risk 🟡",
        2: "High Risk 🔴"
    }
    st.sidebar.success(f"Predicted Risk Level: {risk_labels.get(prediction, 'Unknown')}")
    recommendation = patrol_recommendation(prediction)
    st.sidebar.info(f"Patrol Recommendation: {recommendation}")

for _ in range(1):   # increase number to push further down
    st.sidebar.write("")
# Sidebar Footer (Always Visible)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='text-align:center; color:#9ca3af; font-size:13px;'>"
    "Team – Neural Navigators ~ VSIT 2026"
    "</p>",
    unsafe_allow_html=True
)


# ---------------- PREDICTIVE LOGIC ----------------
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


map_center = [df["latitude"].mean(), df["longitude"].mean()]
crime_map = folium.Map(location=map_center, zoom_start=12, control_scale=True)


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

for cluster_id in df["cluster"].unique():
    cluster_df = df[df["cluster"] == cluster_id]
    center = [cluster_df["latitude"].mean(), cluster_df["longitude"].mean()]
    ratio = night_crime_ratio(df, cluster_id)
    risk = classify_risk(ratio)
    patrol = hotspot_recommendation(risk)

    color_map = {"RED": "#dc2626", "YELLOW": "#f59e0b", "GREEN": "#16a34a"}

    folium.Circle(
        location=center,
        radius=700,
        color=risk.lower(),
        fill=True,
        fill_opacity=0.45,
        popup=f"<b>{risk} Risk Area</b><br>Patrol: {patrol}"
    ).add_to(crime_map)

st.components.v1.html(
    crime_map._repr_html_(),
    height=750,
    scrolling=False
)
