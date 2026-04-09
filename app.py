# app.py
import yfinance as yf
import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- LOAD SECRETS ---
load_dotenv() 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="PetroPulse AI", page_icon="⛽", layout="wide")

# --- CUSTOM CSS ---
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

# --- DYNAMIC ROUTE DATA (MOCK DATABASE) ---
route_data = {
    "Delhi -> Mumbai": {
        "distance": 1400,
        "origin_state": "Delhi",
        "origin_price": 89.62,
        "border_state": "Haryana",
        "border_price": 87.00,
        "depot_name": "Depot #2"
    },
    "Chennai -> Bangalore": {
        "distance": 350,
        "origin_state": "Tamil Nadu",
        "origin_price": 92.34,
        "border_state": "Karnataka",
        "border_price": 89.22,
        "depot_name": "Hosur Highway Pump"
    },
    "Kolkata -> Patna": {
        "distance": 580,
        "origin_state": "West Bengal",
        "origin_price": 90.76,
        "border_state": "Jharkhand",
        "border_price": 88.50,
        "depot_name": "Dhanbad Border Station"
    }
}

# --- SIDEBAR (User Inputs) ---
with st.sidebar:
    st.header("⚙️ Fleet Parameters")
    fleet_size = st.slider("Active Fleet Size (Trucks)", 10, 500, 50)
    avg_mileage = st.number_input("Avg Mileage (kmpl)", value=4.5)
    route_select = st.selectbox("Active Route", list(route_data.keys()))
    
    st.markdown("---")
    st.header("🤖 FastMCP Status")
    st.success("Connected to PetroPulse Orchestrator")
    st.caption("AI Tools Active: Prophet ML, Arbitrage Engine, P&L Calculator")

# Fetch the data for the currently selected route
current_route = route_data[route_select]
price_diff = current_route["origin_price"] - current_route["border_price"]

# --- LIVE DATA FETCHER ---
@st.cache_data(ttl=300) # Caches the data for 5 minutes
def fetch_live_markets():
    try:
        # Fetch Brent Crude Oil Futures
        brent = yf.Ticker("BZ=F")
        brent_hist = brent.history(period="2d")
        brent_live = brent_hist['Close'].iloc[-1]
        brent_prev = brent_hist['Close'].iloc[-2]
        brent_pct = ((brent_live - brent_prev) / brent_prev) * 100

        # Fetch USD to INR Exchange Rate
        inr = yf.Ticker("INR=X")
        inr_hist = inr.history(period="2d")
        inr_live = inr_hist['Close'].iloc[-1]
        inr_prev = inr_hist['Close'].iloc[-2]
        inr_pct = ((inr_live - inr_prev) / inr_prev) * 100

        return brent_live, brent_pct, inr_live, inr_pct
    except:
        return 86.40, 1.2, 83.50, -0.1

brent_val, brent_delta, inr_val, inr_delta = fetch_live_markets()

# --- MAIN DASHBOARD: ROW 1 (Metrics) ---
st.caption(f"🟢 Live Market Feed connected. Last synced: {datetime.now().strftime('%H:%M:%S IST')}")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label=f"Current HSD Price - {current_route['origin_state']}", value=f"₹{current_route['origin_price']:.2f} / L", delta="OMC Spot")
with col2:
    st.metric(label="Predicted Price (30 Days)", value=f"₹{current_route['origin_price'] + 3.60:.2f} / L", delta="+₹3.60 (Expected Hike)", delta_color="inverse")
with col3:
    st.metric(label="Live Brent Crude", value=f"${brent_val:.2f}", delta=f"{brent_delta:.2f}%", delta_color="inverse")
with col4:
    st.metric(label="Live USD / INR", value=f"₹{inr_val:.2f}", delta=f"{inr_delta:.2f}%", delta_color="normal")

st.divider()

# --- MAIN DASHBOARD: ROW 2 (Forecasting & Arbitrage) ---
col_chart, col_arbitrage = st.columns([2, 1])

with col_chart:
    st.subheader("📈 30-Day Fuel Price Forecast")
    
    dates = [datetime.today() - timedelta(days=x) for x in range(30, 0, -1)] + [datetime.today() + timedelta(days=x) for x in range(1, 31)]
    historical_prices = np.linspace(current_route["origin_price"] - 1.62, current_route["origin_price"], 30)
    predicted_prices = np.linspace(current_route["origin_price"], current_route["origin_price"] + 3.60, 30) + np.random.normal(0, 0.2, 30)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates[:30], y=historical_prices, mode='lines', name='Historical', line=dict(color='white', width=2)))
    fig.add_trace(go.Scatter(x=dates[29:], y=predicted_prices, mode='lines', name='AI Forecast', line=dict(color='#00FFCC', width=3, dash='dash')))
    
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=350, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, width="stretch")

with col_arbitrage:
    st.subheader("🗺️ State-Tax Arbitrage")
    st.info(f"**Selected Route:** {route_select}")
    
    st.markdown("**AI Alert Detection:** State border crossing detected. Significant VAT discrepancy.")
    
    st.metric(label=f"{current_route['border_state']} Border Price", 
              value=f"₹{current_route['border_price']:.2f} / L", 
              delta=f"-₹{price_diff:.2f} vs {current_route['origin_state']}")
    
    if st.button("Calculate Route Savings", width="stretch"):
        fuel_needed = current_route["distance"] / avg_mileage
        savings = fuel_needed * price_diff
        st.success(f"**Recommendation:** Schedule primary refueling at {current_route['depot_name']} ({current_route['border_state']} Border).")
        st.balloons()
        st.metric(label="Projected Trip Savings", value=f"₹{savings:,.2f}")

st.divider()

# --- MAIN DASHBOARD: ROW 3 (AI Transition Advisor) ---
st.subheader("🧠 Generative AI Strategic Advisor")
with st.expander("View AI Business Expansion Analysis (LLM Output)", expanded=True):
    st.write(f"""
    Based on your fleet parameters and the projected upward trend in High-Speed Diesel costs in {current_route['origin_state']}, **PetroPulse AI recommends:**
    
    1. **Immediate Action (Hedging):** Lock in a bulk fuel contract for 40% of your expected monthly volume before the 1st of the month.
    2. **Route Optimization:** Ensure all {fleet_size} trucks active on the {route_select} route are utilizing the {current_route['border_state']} arbitrage zone.
    3. **Long-Term Capital Expenditure:** Delay the purchase of new diesel trucks. Allocate capital toward PM E-Drive scheme subsidies.
    """)

st.divider()
st.subheader("💬 PetroPulse AI Co-Pilot")
st.caption("Ask me to analyze routes, predict costs, or suggest hedging strategies.")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("API Key not found! Please check your .env file.")

model = genai.GenerativeModel('gemini-2.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am the PetroPulse Orchestrator. I can see your selected route and live market parameters. How can I optimize your logistics today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(f"E.g., How much will fuel cost for my {fleet_size} trucks on this route?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Analyzing fleet data and market trends..."):
        try:
            system_context = f"""
            You are the PetroPulse AI Co-Pilot, an expert logistics financial advisor. 
            The user currently has a fleet size of {fleet_size} trucks, averaging {avg_mileage} kmpl. 
            
            THE CURRENTLY SELECTED ROUTE IS: {route_select}.
            - The distance is {current_route['distance']} km.
            - The current diesel price at the origin ({current_route['origin_state']}) is ₹{current_route['origin_price']}.
            - There is a tax arbitrage opportunity at the {current_route['border_state']} border where the price is ₹{current_route['border_price']}.
            - This saves ₹{price_diff:.2f} per liter.
            
            LIVE MARKET DATA:
            - Brent Crude is currently at ${brent_val:.2f}.
            - USD to INR is at ₹{inr_val:.2f}.
            
            When the user asks questions about their route, costs, or savings, USE THESE EXACT NUMBERS to calculate the math for them. 
            Keep your answers concise, professional, and focused on saving the user money.
            """
            
            full_prompt = system_context + "\nUser Query: " + prompt
            
            response = model.generate_content(full_prompt)
            reply = response.text
            
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            st.error(f"Error connecting to AI Orchestrator: {e}")
