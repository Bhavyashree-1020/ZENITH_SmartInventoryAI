import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from src.model import predict_demand

st.set_page_config(page_title="Smart Inventory System", layout="wide")

st.title("📦 Smart Inventory & Demand Prediction System")

# Inputs
st.sidebar.header("Input Parameters")

month = st.sidebar.slider("Month", 1, 12, 5)
weekday = st.sidebar.slider("Weekday (0=Mon)", 0, 6, 2)
stock = st.sidebar.slider("Current Stock", 0, 200, 50)

# Predict
if st.button("Predict Demand"):
    demand, reorder = predict_demand(month, weekday, stock)

    st.subheader("📊 Results")

    col1, col2 = st.columns(2)

    col1.metric("Predicted Demand", demand)
    col2.metric("Reorder Quantity", reorder)

    if reorder > 0:
        st.error("⚠️ Low Stock! Reorder Required")
    else:
        st.success("✅ Stock is sufficient")