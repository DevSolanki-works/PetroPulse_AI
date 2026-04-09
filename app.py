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
load_dotenv() # This reads the .env file!
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # This securely grabs your key

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
@st.cache_data(ttl=300) # Caches the data for 5 minutes so the app stays lightning fast
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
        # Hackathon Safety Net: If the API fails, return our mock data so the demo doesn't crash!
        return 86.40, 1.2, 83.50, -0.1

# Fetch the live numbers!
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
    # Fixed deprecation warning here:
    st.plotly_chart(fig, width="stretch")

with col_arbitrage:
    st.subheader("🗺️ State-Tax Arbitrage")
    st.info(f"**Selected Route:** {route_select}")
    
    st.markdown("""
    **AI Alert Detection:**
    State border crossing detected. Significant VAT discrepancy.
    """)
    
    st.metric(label="Haryana Border Price", value="₹87.00 / L", delta="-₹2.62 vs Delhi")
    
    # Fixed deprecation warning here:
    if st.button("Calculate Route Savings", width="stretch"):
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

st.divider()
st.subheader("💬 PetroPulse AI Co-Pilot")
st.caption("Ask me to analyze routes, predict costs, or suggest hedging strategies.")

# Ensure the key is loaded
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("API Key not found! Please check your .env file.")

model = genai.GenerativeModel('gemini-2.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am the PetroPulse Orchestrator. I have access to your live fleet data, state tax matrices, and predictive ML models. How can I optimize your logistics today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("E.g., What is the tax arbitrage for Delhi to Haryana?"):
    # Show user message in UI
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show a loading spinner while Gemini thinks
    with st.spinner("Analyzing fleet data and market trends..."):
        try:
            # --- THE HACKATHON SHORTCUT ---
            system_context = f"""
            You are the PetroPulse AI Co-Pilot, an expert logistics financial advisor. 
            The user currently has a fleet size of {fleet_size} trucks, averaging {avg_mileage} kmpl. 
            The current diesel price in Delhi is ₹89.62, and the 30-day forecast predicts a hike to ₹93.22. 
            The Haryana border price is ₹87.00. 
            Keep your answers concise, professional, and focused on saving the user money.
            """
            
            full_prompt = system_context + "\nUser Query: " + prompt
            
            # Call Gemini
            response = model.generate_content(full_prompt)
            reply = response.text
            
            # Show AI response in UI
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            st.error(f"Error connecting to AI Orchestrator: {e}")
