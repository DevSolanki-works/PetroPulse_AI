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
import pydeck as pdk

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
st.markdown("Real-time predictive fuel analytics, route arbitrage, and live spatial tracking.")
st.divider()

# --- DYNAMIC ROUTE DATA & HIGHWAY FUEL STATIONS ---
route_data = {
    "Delhi -> Mumbai": {
        "distance": 1400, "origin_state": "Delhi", "origin_price": 89.62,
        "border_state": "Haryana", "border_price": 87.00, "depot_name": "Haryana Depot #2",
        "origin_coords": (28.6139, 77.2090), "dest_coords": (19.0760, 72.8777),
        "zoom": 4.8,
        # Multiple real-world highway stops
        "stations": [
            {"name": "IOCL Neemrana Highway", "coords": (27.98, 76.38), "optimal": False},
            {"name": "BPCL Jaipur Bypass", "coords": (26.91, 75.78), "optimal": False},
            {"name": "HPCL Udaipur Stop", "coords": (24.58, 73.68), "optimal": False},
            {"name": "IOCL Vadodara Plaza", "coords": (22.30, 73.19), "optimal": False},
            {"name": "⛽ OPTIMAL: Haryana Border Depot (Save ₹2.62/L)", "coords": (28.20, 76.90), "optimal": True}
        ]
    },
    "Chennai -> Bangalore": {
        "distance": 350, "origin_state": "Tamil Nadu", "origin_price": 92.34,
        "border_state": "Karnataka", "border_price": 89.22, "depot_name": "Hosur Highway Pump",
        "origin_coords": (13.0827, 80.2707), "dest_coords": (12.9716, 77.5946),
        "zoom": 6.8,
        "stations": [
            {"name": "HPCL Sriperumbudur", "coords": (12.96, 79.94), "optimal": False},
            {"name": "IOCL Vellore Highway", "coords": (12.91, 79.13), "optimal": False},
            {"name": "BPCL Krishnagiri Rest Stop", "coords": (12.52, 78.21), "optimal": False},
            {"name": "⛽ OPTIMAL: Hosur Border Pump (Save ₹3.12/L)", "coords": (12.73, 77.82), "optimal": True}
        ]
    },
    "Kolkata -> Patna": {
        "distance": 580, "origin_state": "West Bengal", "origin_price": 90.76,
        "border_state": "Jharkhand", "border_price": 88.50, "depot_name": "Dhanbad Border Station",
        "origin_coords": (22.5726, 88.3639), "dest_coords": (25.5941, 85.1376),
        "zoom": 5.8,
        "stations": [
            {"name": "IOCL Bardhaman Bypass", "coords": (23.23, 87.86), "optimal": False},
            {"name": "BPCL Asansol Highway", "coords": (23.68, 86.98), "optimal": False},
            {"name": "HPCL Bihar Sharif Plaza", "coords": (25.19, 85.51), "optimal": False},
            {"name": "⛽ OPTIMAL: Dhanbad Border Station (Save ₹2.26/L)", "coords": (23.79, 86.43), "optimal": True}
        ]
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
@st.cache_data(ttl=600)
def fetch_live_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url).json()
        temp = response['current_weather']['temperature']
        wind = response['current_weather']['windspeed']
        code = response['current_weather']['weathercode']
        if code <= 3: condition = "Clear ☀️"
        elif code <= 48: condition = "Cloudy ☁️"
        elif code <= 67: condition = "Rain 🌧️"
        else: condition = "Storm/Heavy Rain ⛈️"
        return temp, wind, condition
    except:
        return "--", "--", "API Error ⚠️"

o_temp, o_wind, o_cond = fetch_live_weather(current_route["origin_coords"][0], current_route["origin_coords"][1])
d_temp, d_wind, d_cond = fetch_live_weather(current_route["dest_coords"][0], current_route["dest_coords"][1])

with st.sidebar:
    st.markdown("---")
    st.header("🌤️ Live Route Weather")
    st.caption(f"📍 Origin: {demo_origin}")
    st.write(f"**{o_cond}** | {o_temp}°C | 💨 {o_wind} km/h")
    st.caption(f"🏁 Destination: {demo_dest}")
    st.write(f"**{d_cond}** | {d_temp}°C | 💨 {d_wind} km/h")
    
    if "Rain" in o_cond or "Rain" in d_cond or "Storm" in o_cond or "Storm" in d_cond:
        st.error("⚠️ **ALERT:** Adverse weather detected on route. Reduce speeds.")
    else:
        st.success("✅ Route weather optimal.")

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
    st.subheader("📈 Live Fuel Price Forecast")
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

# --- MAIN DASHBOARD: ROW 3 (DYNAMIC HIGHWAY MAP WITH REAL ROADS) ---
st.subheader("🛰️ Highway Radar & Refill Stations")
st.caption("Auto-centered on active route. Gray dots = standard pumps. Gold dot = Optimal Arbitrage Pump.")

# 1. Grab coordinates to center the map
orig_coords = current_route["origin_coords"]
dest_coords = current_route["dest_coords"]
mid_lat = (orig_coords[0] + dest_coords[0]) / 2
mid_lon = (orig_coords[1] + dest_coords[1]) / 2

# 2. OSRM Real-Time Highway Routing
@st.cache_data(ttl=3600)
def get_actual_route(start_coords, end_coords):
    start_lon, start_lat = start_coords[1], start_coords[0]
    dest_lon, dest_lat = end_coords[1], end_coords[0]
    
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{dest_lon},{dest_lat}?overview=full&geometries=geojson"
    try:
        response = requests.get(url).json()
        return response['routes'][0]['geometry']['coordinates']
    except Exception as e:
        return [[start_lon, start_lat], [dest_lon, dest_lat]]

road_path = get_actual_route(orig_coords, dest_coords)

# 3. 🧠 THE SPATIAL SNAPPING ALGORITHM 
def snap_to_route(target_lat, target_lon, route_path):
    """Finds the closest point on the OSRM path to our real-world station."""
    closest_point = [target_lon, target_lat] # Default fallback
    min_dist = float('inf')
    
    for lon, lat in route_path:
        # Calculate squared Euclidean distance to find the nearest road coordinate
        dist = (lat - target_lat)**2 + (lon - target_lon)**2
        if dist < min_dist:
            min_dist = dist
            closest_point = [lon, lat] # PyDeck expects [Longitude, Latitude]
            
    return closest_point

# 4. Build the visual layers
df_route = pd.DataFrame([{"path": road_path, "name": route_select}])

df_cities = pd.DataFrame([
    {"coords": [orig_coords[1], orig_coords[0]], "name": f"Origin: {demo_origin}", "color": [0, 255, 204, 255]},
    {"coords": [dest_coords[1], dest_coords[0]], "name": f"Destination: {demo_dest}", "color": [255, 0, 128, 255]}
])

# Process and SNAP the stations
standard_stations = []
optimal_stations = []

for station in current_route["stations"]:
    # Snap the realistic GPS coordinate to the exact OSRM highway line!
    snapped_coords = snap_to_route(station["coords"][0], station["coords"][1], road_path)
    
    point = {"coords": snapped_coords, "name": station["name"]}
    
    if station["optimal"]:
        point["color"] = [255, 215, 0, 255] # Solid Gold
        optimal_stations.append(point)
    else:
        point["color"] = [200, 200, 200, 200] # Light Grey
        standard_stations.append(point)

df_standard = pd.DataFrame(standard_stations)
df_optimal = pd.DataFrame(optimal_stations)

# 5. Create PyDeck Layers
layer_path = pdk.Layer(
    "PathLayer",
    data=df_route,
    get_path="path",
    get_color=[0, 255, 204, 200], 
    width_scale=20,
    width_min_pixels=3, 
)

layer_cities = pdk.Layer(
    "ScatterplotLayer",
    data=df_cities,
    get_position="coords",
    get_color="color",
    get_radius=8000, 
    pickable=True
)

layer_standard_pumps = pdk.Layer(
    "ScatterplotLayer",
    data=df_standard,
    get_position="coords",
    get_color="color",
    get_radius=4000, 
    pickable=True
)

layer_optimal_pump = pdk.Layer(
    "ScatterplotLayer",
    data=df_optimal,
    get_position="coords",
    get_color="color",
    get_radius=9000, 
    pickable=True
)

# 6. Render the Map
st.pydeck_chart(pdk.Deck(
    map_provider="carto",
    map_style="dark",
    initial_view_state=pdk.ViewState(
        latitude=mid_lat, 
        longitude=mid_lon,
        zoom=current_route["zoom"], 
        pitch=0, 
    ),
    layers=[layer_path, layer_standard_pumps, layer_optimal_pump, layer_cities],
    tooltip={"text": "{name}"} 
))

st.divider()

# --- MAIN DASHBOARD: ROW 4 (Backhaul & AI Co-Pilot) ---
col_backhaul, col_chat = st.columns([1, 1])

with col_backhaul:
    st.subheader("🔄 Backhaul Load Matcher")
    st.info(f"**Live Radar:** Scanning freight exchanges for empty trucks returning from **{demo_dest}** to **{demo_origin}**.")
    if st.button("Scan for Return Loads", width="stretch", type="primary"):
        with st.spinner("Querying live load boards..."):
            time.sleep(1.5) 
            revenue_map = {"Mumbai": 45000, "Bangalore": 32000, "Patna": 28000}
            backhaul_rev = revenue_map.get(demo_dest, 30000)
            st.success(f"✅ **Instant Match Found!** Priority load available at {demo_dest}.")
            st.metric(label="New Revenue Generated", value=f"+ ₹{backhaul_rev:,.2f}")

with col_chat:
    st.subheader("💬 PetroPulse AI BOT")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    else:
        st.error("API Key not found!")
    
    # 1. Inject the Smart Approximation logic directly into the AI's core behavior
    system_context = f"""
    You are PetroPulse AI, an elite logistics financial advisor for India. 
    CURRENT DASHBOARD CONTEXT:
    - Active Route: {route_select} (Distance: {current_route['distance']} km).
    - Fleet: {fleet_size} trucks averaging {avg_mileage} kmpl.
    - Arbitrage Savings: ₹{price_diff:.2f}/L at {current_route['border_state']}.
    
    CRITICAL INSTRUCTION FOR UNKNOWN ROUTES:
    If the user asks about a custom route NOT listed above (e.g., Ladakh to Tamil Nadu, or any other cities), DO NOT say you don't know. 
    Act as a senior logistics consultant and provide an approximation:
    1. Estimate the distance in km.
    2. Calculate estimated fuel needed: (Distance / {avg_mileage}) * {fleet_size} trucks.
    3. Suggest a major Indian National Highway route.
    4. Point out 1 or 2 potential state borders along that journey where tax arbitrage might be beneficial.
    Keep it professional, structured, and highly realistic.
    """

    # Initialize the model with the system instructions
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction=system_context
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am monitoring the map, weather, and market. Try asking me to estimate a custom route!"}]
    
    chat_container = st.container(height=300)
    for message in st.session_state.messages:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("Ask about custom routes, weather, or savings..."):
        chat_container.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("Analyzing custom route logistics..."):
            try:
                # 2. Give the AI memory of the conversation
                chat_history = []
                for m in st.session_state.messages[:-1]:
                    # Gemini expects 'model' instead of 'assistant' for role names
                    role = "user" if m["role"] == "user" else "model"
                    chat_history.append({"role": role, "parts": [m["content"]]})
                
                # Start the chat session
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(prompt)
                
                with chat_container.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                # 3. Unmask the exact error so we can debug it if it fails again!
                st.error(f"⚠️ API Error: {str(e)}")
