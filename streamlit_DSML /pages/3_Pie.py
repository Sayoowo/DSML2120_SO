import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.title("🥧 How I Spend My Week")

# Find data/pie_demo.csv (one level up from the pages folder)
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "pie_demo.csv"

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(f"Could not find {DATA_PATH}. Make sure pie_demo.csv is in the data folder.")
    st.stop()

# ---------- Interactive controls ----------
categories = df["Activity"].tolist()
selected = st.multiselect(
    "Choose which activities to include:",
    options=categories,
    default=categories,
)

show_labels = st.checkbox("Show percentage labels", value=True)

filtered = df[df["Activity"].isin(selected)].copy()

if filtered.empty:
    st.warning("Select at least one activity to see the chart.")
    st.stop()

filtered["Percent"] = filtered["Hours"] / filtered["Hours"].sum()

# ---------- Pie chart ----------
base = alt.Chart(filtered).encode(
    theta=alt.Theta("Hours:Q", stack=True),
    color=alt.Color("Activity:N", legend=alt.Legend(title="Activity")),
    tooltip=[
        alt.Tooltip("Activity:N"),
        alt.Tooltip("Hours:Q"),
        alt.Tooltip("Percent:Q", format=".1%"),
    ],
)

pie = base.mark_arc(outerRadius=140)
chart = pie

if show_labels:
    text = base.mark_text(radius=170, size=13).encode(
        text=alt.Text("Percent:Q", format=".0%")
    )
    chart = pie + text

st.altair_chart(chart, use_container_width=True)

# ---------- Data table ----------
with st.expander("See the data"):
    st.dataframe(filtered[["Activity", "Hours"]], hide_index=True)
