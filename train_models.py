# train_models.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import pickle

print("🧠 Starting PetroPulse ML Pipeline...")

# ==========================================
# MODEL 1: Fuel Efficiency Predictor
# ==========================================
print("\n--- Training Route Optimization Model ---")
try:
    # MAGIC FIX: Auto-detects spaces/tabs instead of just commas!
    df_routes = pd.read_csv("Truck-route.csv", sep=None, engine='python')
    df_routes.columns = df_routes.columns.str.strip() # Remove invisible spaces
    
    # Drop rows where target data is missing
    df_routes = df_routes.dropna(subset=['distance_km', 'fuel_consumed_litres'])
    
    # Separate Inputs (X) and Output (y)
    X_routes = df_routes[['distance_km']]
    y_routes = df_routes['fuel_consumed_litres']
    
    # Train the Model
    route_model = RandomForestRegressor(n_estimators=100, random_state=42)
    route_model.fit(X_routes, y_routes)
    
    # Save the brain
    with open('route_model.pkl', 'wb') as f:
        pickle.dump(route_model, f)
    print("✅ SUCCESS: route_model.pkl created from Truck-route.csv!")

except Exception as e:
    print(f"❌ ERROR on Route Model: {e}")

# ==========================================
# MODEL 2: Truck Health Predictor
# ==========================================
print("\n--- Training Truck Health Model ---")
try:
    df_health = pd.read_csv("Truck-data.csv", sep=None, engine='python')
    df_health.columns = df_health.columns.str.strip()
    df_health = df_health.dropna()
    
    # Needs columns EXACTLY named: km_since_service, load_weight_tons, breakdown_risk
    X_health = df_health[['km_since_service', 'load_weight_tons']]
    y_health = df_health['breakdown_risk'] 
    
    health_model = RandomForestClassifier(n_estimators=100, random_state=42)
    health_model.fit(X_health, y_health)
    
    with open('health_model.pkl', 'wb') as f:
        pickle.dump(health_model, f)
    print("✅ SUCCESS: health_model.pkl created from Truck-data.csv!")

except Exception as e:
    print(f"⚠️ Warning: Could not parse Truck-data.csv columns ({e}).")
    print("Generating backup synthetic Health Model for the Hackathon Demo...")
    # FALLBACK: Generates a working model if your CSV columns don't match
    X_fake = pd.DataFrame({'km_since_service': np.random.uniform(0, 50000, 100), 
                           'load_weight_tons': np.random.uniform(10, 40, 100)})
    y_fake = np.where(X_fake['km_since_service'] > 35000, 1, 0)
    
    backup_model = RandomForestClassifier(n_estimators=50, random_state=42)
    backup_model.fit(X_fake, y_fake)
    with open('health_model.pkl', 'wb') as f:
        pickle.dump(backup_model, f)
    print("✅ SUCCESS: Backup health_model.pkl created!")

print("\n🎉 ML Pipeline Execution Finished!")