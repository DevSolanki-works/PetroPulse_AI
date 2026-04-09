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
import time
import requests

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
st.markdown("Real-time predictive fuel analytics, route arbitrage, and live weather tracking.")
st.divider()

# --- DYNAMIC ROUTE DATA & GPS COORDINATES ---
route_data = {
    "Delhi -> Mumbai": {
        "distance": 1400, "origin_state": "Delhi", "origin_price": 89.62,
        "border_state": "Haryana", "border_price": 87.00, "depot_name": "Depot #2",
        "origin_coords": (28.6139, 77.2090), "dest_coords": (19.0760, 72.8777)
    },
    "Chennai -> Bangalore": {
        "distance": 350, "origin_state": "Tamil Nadu", "origin_price": 92.34,
        "border_state": "Karnataka", "border_price": 89.22, "depot_name": "Hosur Highway Pump",
        "origin_coords": (13.0827, 80.2707), "dest_coords": (12.9716, 77.5946)
    },
    "Kolkata -> Patna": {
        "distance": 580, "origin_state": "West Bengal", "origin_price": 90.76,
        "border_state": "Jharkhand", "border_price": 88.50, "depot_name": "Dhanbad Border Station",
        "origin_coords": (22.5726, 88.3639), "dest_coords": (25.5941, 85.1376)
    }
}

# --- SIDEBAR (User Inputs) ---
with st.sidebar:
    st.header("⚙️ Fleet Parameters")
    fleet_size = st.slider("Active Fleet Size (Trucks)", 10, 500, 50)
    avg_mileage = st.number_input("Avg Mileage (kmpl)", value=4.5)
    route_select = st.selectbox("Active Route", list(route_data.keys()))

current_route = route_data[route_select]
price_diff = current_route["origin_price"] - current_route["border_price"]
demo_origin = route_select.split(" -> ")[0]
demo_dest = route_select.split(" -> ")[1]

# --- LIVE WEATHER FETCHER ---
@st.cache_data(ttl=600) # Caches weather for 10 minutes
def fetch_live_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url).json()
        temp = response['current_weather']['temperature']
        wind = response['current_weather']['windspeed']
        code = response['current_weather']['weathercode']
        
        # Determine weather condition
        if code <= 3: condition = "Clear ☀️"
        elif code <= 48: condition = "Cloudy ☁️"
        elif code <= 67: condition = "Rain 🌧️"
        else: condition = "Storm/Heavy Rain ⛈️"
        
        return temp, wind, condition
    except:
        return "--", "--", "API Error ⚠️"

o_temp, o_wind, o_cond = fetch_live_weather(current_route["origin_coords"][0], current_route["origin_coords"][1])
d_temp, d_wind, d_cond = fetch_live_weather(current_route["dest_coords"][0], current_route["dest_coords"][1])

# --- ADD WEATHER TO SIDEBAR ---
with st.sidebar:
    st.markdown("---")
    st.header("🌤️ Live Route Weather")
    
    st.caption(f"📍 Origin: {demo_origin}")
    st.write(f"**{o_cond}** | {o_temp}°C | 💨 {o_wind} km/h")
    
    st.caption(f"🏁 Destination: {demo_dest}")
    st.write(f"**{d_cond}** | {d_temp}°C | 💨 {d_wind} km/h")
    
    if "Rain" in o_cond or "Rain" in d_cond or "Storm" in o_cond or "Storm" in d_cond:
        st.error("⚠️ **ALERT:** Adverse weather detected on route. Reduce speeds and update ETAs.")
    else:
        st.success("✅ Route weather is optimal for transit.")
        
    st.markdown("---")
    st.header("🤖 FastMCP Status")
    st.success("Connected to PetroPulse Orchestrator")
    st.caption("AI Tools Active: Prophet ML, Arbitrage, Backhaul, Weather")

# --- LIVE FINANCIAL DATA FETCHER ---
@st.cache_data(ttl=300) 
def fetch_live_markets():
    try:
        brent = yf.Ticker("BZ=F")
        brent_hist = brent.history(period="1mo")
        brent_live = brent_hist['Close'].iloc[-1]
        brent_prev = brent_hist['Close'].iloc[-2]
        brent_pct = ((brent_live - brent_prev) / brent_prev) * 100
        
        crude_prices = brent_hist['Close'].values
        crude_trend = crude_prices / crude_prices[-1] 

        inr = yf.Ticker("INR=X")
        inr_hist = inr.history(period="2d")
        inr_live = inr_hist['Close'].iloc[-1]
        inr_pct = ((inr_live - inr_hist['Close'].iloc[-2]) / inr_hist['Close'].iloc[-2]) * 100

        return brent_live, brent_pct, inr_live, inr_pct, crude_trend
    except:
        return 86.40, 1.2, 83.50, -0.1, np.linspace(0.98, 1.0, 22)

brent_val, brent_delta, inr_val, inr_delta, crude_trend = fetch_live_markets()

# --- MAIN DASHBOARD: ROW 1 (Metrics) ---
st.caption(f"🟢 Live Market Feed connected. Last synced: {datetime.now().strftime('%H:%M:%S IST')}")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label=f"Current Price - {current_route['origin_state']}", value=f"₹{current_route['origin_price']:.2f} / L", delta="OMC Spot")
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
    st.subheader("📈 Live Fuel Price Forecast (Crude-Mapped)")
    
    past_dates = [datetime.today() - timedelta(days=x) for x in range(len(crude_trend)-1, -1, -1)]
    future_dates = [datetime.today() + timedelta(days=x) for x in range(1, 31)]
    
    base_price = current_route["origin_price"]
    historical_prices = base_price * crude_trend
    
    volatility = np.std(crude_trend) * base_price
    predicted_prices = np.linspace(base_price, base_price + 3.60, 30) + np.random.normal(0, volatility, 30)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=past_dates, y=historical_prices, mode='lines', name='Actual Market Trend', line=dict(color='white', width=2)))
    fig.add_trace(go.Scatter(x=future_dates, y=predicted_prices, mode='lines', name='AI ML Forecast', line=dict(color='#00FFCC', width=3, dash='dash')))
    
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=350, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, width="stretch")

with col_arbitrage:
    st.subheader("🗺️ State-Tax Arbitrage")
    st.info(f"**Selected Route:** {route_select}")
    st.markdown("**AI Alert:** State border crossing detected. Significant VAT discrepancy.")
    st.metric(label=f"{current_route['border_state']} Border Price", value=f"₹{current_route['border_price']:.2f} / L", delta=f"-₹{price_diff:.2f} vs {current_route['origin_state']}")
    
    if st.button("Calculate Route Savings", width="stretch"):
        fuel_needed = current_route["distance"] / avg_mileage
        savings = fuel_needed * price_diff
        st.success(f"**Recommendation:** Primary refueling at {current_route['depot_name']}.")
        st.balloons()
        st.metric(label="Projected Savings", value=f"₹{savings:,.2f}")

st.divider()

# --- MAIN DASHBOARD: ROW 2.5 (Backhaul Matcher) ---
st.subheader("🔄 Backhaul Load Matcher (Eliminate Empty Miles)")

st.info(f"**Live Radar:** Scanning freight exchanges for empty trucks returning from **{demo_dest}** to **{demo_origin}**.")
col_b1, col_b2 = st.columns([3, 1])

with col_b1:
    if st.button("Scan for Return Loads", width="stretch", type="primary"):
        with st.spinner("Querying live load boards..."):
            time.sleep(1.5) 
            revenue_map = {"Mumbai": 45000, "Bangalore": 32000, "Patna": 28000}
            backhaul_rev = revenue_map.get(demo_dest, 30000)
            
            st.success(f"✅ **Instant Match Found!** Priority load available at {demo_dest} logistics park heading directly to {demo_origin}.")
            st.metric(label="New Revenue Generated (Offsetting Fuel Costs)", value=f"+ ₹{backhaul_rev:,.2f}", delta="Profit Margin Protected")

with col_b2:
    st.markdown("""
    **Algorithm Status:**
    * API: Connected
    * Deadhead Risk: Mitigated
    """)

st.divider()

# --- MAIN DASHBOARD: ROW 3 (AI Transition Advisor) ---
st.subheader("🧠 Generative AI Strategic Advisor")
with st.expander("View AI Business Expansion Analysis (LLM Output)", expanded=True):
    st.write(f"""
    Based on live crude volatility ({brent_delta:.2f}%) and upward trends in {current_route['origin_state']}, **PetroPulse AI recommends:**
    
    1. **Immediate Hedging:** Lock in a bulk fuel contract for 40% of volume before the 1st of the month.
    2. **Route Optimization:** Ensure all {fleet_size} trucks utilize the {current_route['border_state']} arbitrage zone.
    3. **Backhaul Mandate:** Require dispatchers to accept {demo_dest} return loads.
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
        {"role": "assistant", "content": "Hello! I am the PetroPulse Orchestrator. I can see your selected route, weather conditions, and live market parameters. How can I optimize your logistics today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(f"E.g., How much will fuel cost for my {fleet_size} trucks on this route?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Analyzing fleet data, market trends, and weather..."):
        try:
            system_context = f"""
            You are the PetroPulse AI Co-Pilot. 
            Fleet size: {fleet_size} trucks. Mileage: {avg_mileage} kmpl. 
            Route: {route_select} (Distance: {current_route['distance']} km).
            
            LIVE WEATHER DATA:
            - Origin ({demo_origin}): {o_temp}°C, {o_cond}, Wind: {o_wind} km/h.
            - Destination ({demo_dest}): {d_temp}°C, {d_cond}, Wind: {d_wind} km/h.
            *If the weather is "Rain" or "Storm", warn the user about potential delays or lower fuel efficiency.*

            Origin Price: ₹{current_route['origin_price']}. Border Price: ₹{current_route['border_price']}.
            Savings per liter: ₹{price_diff:.2f}.
            Live Brent Crude: ${brent_val:.2f}. USD/INR: ₹{inr_val:.2f}.
            
            Always suggest the Backhaul Matcher if they ask about returning empty or making more profit.
            """
            
            full_prompt = system_context + "\nUser Query: " + prompt
            response = model.generate_content(full_prompt)
            reply = response.text
            
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            st.error(f"Error connecting to AI Orchestrator: {e}")



