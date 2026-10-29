import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

st.set_page_config(page_title="Denver Weather", page_icon="🌤️", layout="wide")
st.title("🌤️ Denver Temperature Over Time (Open-Meteo)")
st.caption("Friendly demo with manual refresh + fallback data so it never crashes.")

lat, lon = 39.7392, -104.9903  # Denver
wurl = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,wind_speed_10m"
        "&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=America/Denver")

# Backup snack, used only if the very first try fails
SAMPLE_WX = pd.DataFrame([{"time": pd.Timestamp("2026-01-01 12:00"),
                           "temperature": 50.0, "wind": 5.0}])

@st.cache_data(ttl=600, show_spinner=False)   # Cache for 10 minutes
def fetch_weather(url: str):
    """Return (df, error_message). Never raise."""
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 429:
            return None, "429 Too Many Requests — try again later"
        r.raise_for_status()
        j = r.json()["current"]
        df = pd.DataFrame([{"time": pd.to_datetime(j["time"]),
                            "temperature": j["temperature_2m"],
                            "wind": j["wind_speed_10m"]}])
        return df, None
    except requests.RequestException as e:
        return None, f"Network/HTTP error: {e}"

# Sticker book: starts empty the first time
if "wx_history" not in st.session_state:
    st.session_state.wx_history = None

# Knobs
st.subheader("🔁 Auto Refresh Settings")
refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)
auto_refresh = st.toggle("Enable auto-refresh", value=False)
if st.button("🔄 Refresh now"):
    st.cache_data.clear()

# Get a new dot
new, err = fetch_weather(wurl)
hist = st.session_state.wx_history

if err:
    st.warning(err)
    if hist is None:
        st.info("Showing sample data until the real weather loads.")
        st.session_state.wx_history = SAMPLE_WX
elif hist is None or hist.equals(SAMPLE_WX):
    st.session_state.wx_history = new          # first real dot (replaces sample)
elif new["time"].iloc[0] > hist["time"].max():
    st.session_state.wx_history = pd.concat([hist, new], ignore_index=True)

# Draw the line
hist = st.session_state.wx_history
st.metric("Temperature now", f"{hist['temperature'].iloc[-1]} °F")
fig = px.line(hist, x="time", y="temperature", markers=True,
              title="Denver temperature over time (°F)")
st.plotly_chart(fig, use_container_width=True)
st.dataframe(hist, use_container_width=True)

st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

if auto_refresh:
    time.sleep(refresh_sec)
    st.rerun()