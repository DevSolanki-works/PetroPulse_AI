# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="PetroPulse AI", page_icon="⛽", layout="wide")

# --- CUSTOM CSS (For a sleek SaaS look) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    h1, h2, h3 { color: #00FFCC; }
    .stMetric { background-color: #1E2530; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("⛽ PetroPulse AI: Fleet Command Center")
st.markdown("Real-time predictive fuel analytics and route arbitrage for Indian logistics.")
st.divider()

# --- SIDEBAR (User Inputs) ---
with st.sidebar:
    st.header("⚙️ Fleet Parameters")
    fleet_size = st.slider("Active Fleet Size (Trucks)", 10, 500, 50)
    avg_mileage = st.number_input("Avg Mileage (kmpl)", value=4.5)
    route_select = st.selectbox("Active Route", ["Delhi -> Mumbai", "Chennai -> Bangalore", "Kolkata -> Patna"])
    
    st.markdown("---")
    st.header("🤖 FastMCP Status")
    st.success("Connected to PetroPulse Orchestrator")
    st.caption("AI Tools Active: Prophet ML, Arbitrage Engine, P&L Calculator")

# --- MAIN DASHBOARD: ROW 1 (Metrics) ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Current HSD (Diesel) Price - Delhi", value="₹89.62 / L", delta="Spot Market")
with col2:
    st.metric(label="Predicted Price (30 Days)", value="₹93.22 / L", delta="+₹3.60 (Expected Hike)", delta_color="inverse")
with col3:
    st.metric(label="Brent Crude Future", value="$86.40", delta="+1.2%", delta_color="inverse")
with col4:
    st.metric(label="USD / INR", value="₹83.50", delta="-0.1%", delta_color="normal")

st.divider()

# --- MAIN DASHBOARD: ROW 2 (Forecasting & Arbitrage) ---
col_chart, col_arbitrage = st.columns([2, 1])

with col_chart:
    st.subheader("📈 30-Day Fuel Price Forecast")
    
    # Generating mock time-series data for the demo
    dates = [datetime.today() - timedelta(days=x) for x in range(30, 0, -1)] + [datetime.today() + timedelta(days=x) for x in range(1, 31)]
    historical_prices = np.linspace(88.00, 89.62, 30)
    predicted_prices = np.linspace(89.62, 93.22, 30) + np.random.normal(0, 0.2, 30)
    
    fig = go.Figure()
    # Historical Data
    fig.add_trace(go.Scatter(x=dates[:30], y=historical_prices, mode='lines', name='Historical', line=dict(color='white', width=2)))
    # Predicted Data
    fig.add_trace(go.Scatter(x=dates[29:], y=predicted_prices, mode='lines', name='AI Forecast', line=dict(color='#00FFCC', width=3, dash='dash')))
    
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=350, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_arbitrage:
    st.subheader("🗺️ State-Tax Arbitrage")
    st.info(f"**Selected Route:** {route_select}")
    
    st.markdown("""
    **AI Alert Detection:**
    State border crossing detected. Significant VAT discrepancy.
    """)
    
    st.metric(label="Haryana Border Price", value="₹87.00 / L", delta="-₹2.62 vs Delhi")
    
    if st.button("Calculate Route Savings", use_container_width=True):
        distance = 1400 # Delhi to Mumbai approx
        fuel_needed = distance / avg_mileage
        savings = fuel_needed * 2.62
        st.success(f"**Recommendation:** Schedule primary refueling at Depot #2 (Haryana Border).")
        st.balloons()
        st.metric(label="Projected Trip Savings", value=f"₹{savings:,.2f}")

st.divider()

# --- MAIN DASHBOARD: ROW 3 (AI Transition Advisor) ---
st.subheader("🧠 Generative AI Strategic Advisor")
with st.expander("View AI Business Expansion Analysis (LLM Output)", expanded=True):
    st.write("""
    Based on your fleet parameters and the projected 4% upward trend in High-Speed Diesel costs over the next quarter, **PetroPulse AI recommends:**
    
    1. **Immediate Action (Hedging):** Lock in a bulk fuel contract for 40% of your expected monthly volume before the 1st of the month to offset the anticipated OMC price revision.
    2. **Short-Term Operations:** Shift 15% of your intra-city delivery routes to your existing EV light-commercial vehicles.
    3. **Long-Term Capital Expenditure:** Delay the purchase of 5 new diesel trucks. Allocate that capital toward the newly announced PM E-Drive scheme subsidies for heavy electric commercial vehicles.
    """)
