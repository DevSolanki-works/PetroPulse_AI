# server.py
from mcp.server.fastmcp import FastMCP

# 1. Initialize your Agentic Server
mcp = FastMCP("PetroPulse")

# ==========================================
# TOOL 1: The Predictive ML Forecaster
# ==========================================
@mcp.tool()
def get_diesel_forecast(days_ahead: int) -> dict:
    """
    Predicts the future price of High-Speed Diesel (HSD) for the Indian market.
    Use this tool when the user asks about future fuel prices or when to hedge.
    
    Args:
        days_ahead: Number of days in the future to predict (e.g., 30 for next month).
    """
    # HACKATHON SHORTCUT: We are hardcoding the MVP math for a guaranteed demo win.
    # Later, you can swap this to load your actual .pkl ML model.
    base_price_delhi = 89.62
    
    # Simulating a market spike due to crude oil trends
    predicted_hike = days_ahead * 0.12 
    future_price = base_price_delhi + predicted_hike
    
    return {
        "current_spot_price": base_price_delhi,
        "predicted_future_price": round(future_price, 2),
        "market_trend": "UPWARD - High Volatility",
        "primary_driver": "Rising Brent Crude futures and INR depreciation."
    }

# ==========================================
# TOOL 2: The Route Arbitrage Engine
# ==========================================
@mcp.tool()
def calculate_route_arbitrage(start_city: str, end_city: str, route_distance_km: float, fleet_mileage_kmpl: float) -> dict:
    """
    Calculates fuel savings by exploiting Indian State VAT (Tax) differences on a specific route.
    Use this tool when a user provides travel patterns or asks how to reduce trip costs.
    """
    # Simple fuel calculation
    total_fuel_needed = route_distance_km / fleet_mileage_kmpl
    
    # HACKATHON MOCK DATA: Simulating state tax differences
    # Delhi Diesel: ~₹89.62, Haryana Diesel: ~₹87.00 (Cheaper tax)
    delhi_price = 89.62
    haryana_border_price = 87.00
    
    standard_cost = total_fuel_needed * delhi_price
    optimized_cost = total_fuel_needed * haryana_border_price
    savings = standard_cost - optimized_cost
    
    return {
        "route": f"{start_city} to {end_city}",
        "fuel_required_liters": round(total_fuel_needed, 2),
        "standard_cost_inr": round(standard_cost, 2),
        "optimized_cost_inr": round(optimized_cost, 2),
        "total_savings_inr": round(savings, 2),
        "ai_recommendation": "Do not refuel in Delhi. Route fleet to Haryana border (Depot #2) to exploit state VAT discrepancy."
    }

# ==========================================
# TOOL 3: The Hedging Simulator
# ==========================================
@mcp.tool()
def simulate_hedge(volume_liters: float) -> dict:
    """
    Simulates the financial P&L (Profit and Loss) of buying bulk fuel contracts today versus next month.
    """
    # Pulling from our fake forecast logic
    current_price = 89.62
    predicted_next_month = 93.22 # Projected spike
    
    cost_today = volume_liters * current_price
    cost_next_month = volume_liters * predicted_next_month
    
    money_saved = cost_next_month - cost_today
    
    return {
        "contract_volume": f"{volume_liters} Liters",
        "lock_in_cost_today": round(cost_today, 2),
        "projected_cost_next_month": round(cost_next_month, 2),
        "net_profit_from_hedge": round(money_saved, 2),
        "action": "Immediate Hedge Recommended. Secure bulk supply before the 1st of the month."
    }

if __name__ == "__main__":
    # This runs the MCP server locally using standard input/output
    print("🚀 PetroPulse MCP Server is starting...")
    mcp.run(transport='stdio')
