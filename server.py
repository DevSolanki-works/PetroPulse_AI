# server.py
from mcp.server.fastmcp import FastMCP
import pickle
import pandas as pd

# Initialize your Agentic Server
mcp = FastMCP("PetroPulse")

# --- LOAD ML MODELS INTO MEMORY ---
print("Loading ML Models into Orchestrator...")
try:
    with open('models/route_model.pkl', 'rb') as f:
        route_model = pickle.load(f)
    with open('models/health_model.pkl', 'rb') as f:
        health_model = pickle.load(f)
    print("✅ Machine Learning Models loaded successfully!")
except FileNotFoundError:
    print("⚠️ WARNING: .pkl files not found in /models. You must run train_models.py first!")

# ==========================================
# TOOL 1: ML-Powered Fuel Predictor
# ==========================================
@mcp.tool()
def predict_route_fuel(distance_km: float) -> dict:
    """
    Uses a trained Random Forest Machine Learning model to accurately predict total fuel 
    consumption for a route based strictly on route distance.
    Use this when calculating fuel requirements for a trip.
    """
    input_data = pd.DataFrame({'distance_km': [distance_km]})
    predicted_fuel = route_model.predict(input_data)[0]
    
    return {
        "distance_analyzed_km": distance_km,
        "ml_predicted_fuel_liters": round(predicted_fuel, 2),
        "confidence": "High (Random Forest Regressor trained on logistics routes)"
    }

# ==========================================
# TOOL 2: ML-Powered Fleet Health Risk
# ==========================================
@mcp.tool()
def check_fleet_breakdown_risk(km_since_last_service: float, avg_load_tons: float) -> dict:
    """
    Uses a Machine Learning Classification model to predict if a truck is at high risk 
    of breaking down on the route based on km driven and weight.
    Use this when asked about vehicle health, safety, or maintenance.
    """
    input_data = pd.DataFrame({'km_since_service': [km_since_last_service], 'load_weight_tons': [avg_load_tons]})
    risk_prediction = health_model.predict(input_data)[0]
    
    status = "CRITICAL RISK - Schedule Maintenance" if risk_prediction == 1 else "SAFE - Optimal Health"
    
    return {
        "maintenance_status": status,
        "ai_action_required": risk_prediction == 1
    }

# ==========================================
# TOOL 3: The Arbitrage Engine (Lookup)
# ==========================================
@mcp.tool()
def calculate_arbitrage(distance: float, price_state_a: float, price_state_b: float) -> dict:
    """
    Calculates exact financial savings by using state border tax differences.
    """
    # Baseline fuel calculation
    fuel_needed = distance / 4.5
    cost_a = fuel_needed * price_state_a
    cost_b = fuel_needed * price_state_b
    savings = cost_a - cost_b
    
    return {
        "fuel_needed_liters": round(fuel_needed, 2),
        "savings_inr": round(savings, 2)
    }

# ==========================================
# TOOL 4: Backhaul Load Matcher
# ==========================================
@mcp.tool()
def find_backhaul_load(destination_city: str, origin_city: str, capacity_tons: float) -> dict:
    """
    Finds available freight loads for trucks returning empty from their destination.
    Use this when calculating total round-trip profitability or reducing empty miles.
    """
    # HACKATHON MOCK DATABASE: Simulating a live freight exchange board
    available_loads = [
        {"from": "Mumbai", "to": "Delhi", "commodity": "Electronics", "weight": 18, "revenue": 45000},
        {"from": "Bangalore", "to": "Chennai", "commodity": "Auto Parts", "weight": 22, "revenue": 32000},
        {"from": "Patna", "to": "Kolkata", "commodity": "Textiles", "weight": 15, "revenue": 28000}
    ]
    
    # Search for a match
    for load in available_loads:
        if load["from"] == destination_city and load["to"] == origin_city and load["weight"] <= capacity_tons:
            return {
                "status": "MATCH FOUND",
                "load_details": f"{load['weight']} Tons of {load['commodity']}",
                "pickup": destination_city,
                "dropoff": origin_city,
                "extra_revenue_inr": load["revenue"],
                "recommendation": "Accept load immediately to eliminate deadhead miles."
            }
            
    return {"status": "NO MATCH", "message": "No direct routes found. Consider a triangular route."}

if __name__ == "__main__":
    print("🚀 PetroPulse AI Orchestrator is online...")
    mcp.run(transport='stdio')
