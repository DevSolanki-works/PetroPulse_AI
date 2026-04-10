# train_models.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import pickle
import os

print("🧠 Starting PetroPulse ML Pipeline...")

# Create the models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

# ==========================================
# MODEL 1: Fuel Efficiency Predictor
# ==========================================
print("\n--- Training Route Optimization Model ---")
try:
    # UPDATED PATH: Pointing to the data folder
    df_routes = pd.read_csv("data/Truck-route.csv", sep=None, engine='python')
    df_routes.columns = df_routes.columns.str.strip() 
    df_routes = df_routes.dropna(subset=['distance_km', 'fuel_consumed_litres'])
    
    X_routes = df_routes[['distance_km']]
    y_routes = df_routes['fuel_consumed_litres']
    
    route_model = RandomForestRegressor(n_estimators=100, random_state=42)
    route_model.fit(X_routes, y_routes)
    
    # UPDATED PATH: Saving to the models folder
    with open('models/route_model.pkl', 'wb') as f:
        pickle.dump(route_model, f)
    print("✅ SUCCESS: route_model.pkl created in /models!")

except Exception as e:
    print(f"❌ ERROR on Route Model: {e}")

# ==========================================
# MODEL 2: Truck Health Predictor
# ==========================================
print("\n--- Training Truck Health Model ---")
try:
    # UPDATED PATH: Pointing to the data folder
    df_health = pd.read_csv("data/Truck-data.csv", sep=None, engine='python')
    df_health.columns = df_health.columns.str.strip()
    df_health = df_health.dropna()
    
    X_health = df_health[['km_since_service', 'load_weight_tons']]
    y_health = df_health['breakdown_risk'] 
    
    health_model = RandomForestClassifier(n_estimators=100, random_state=42)
    health_model.fit(X_health, y_health)
    
    # UPDATED PATH: Saving to the models folder
    with open('models/health_model.pkl', 'wb') as f:
        pickle.dump(health_model, f)
    print("✅ SUCCESS: health_model.pkl created in /models!")

except Exception as e:
    print(f"⚠️ Warning: Could not parse Truck-data.csv columns ({e}).")
    print("Generating backup synthetic Health Model for the Hackathon Demo...")
    X_fake = pd.DataFrame({'km_since_service': np.random.uniform(0, 50000, 100), 
                           'load_weight_tons': np.random.uniform(10, 40, 100)})
    y_fake = np.where(X_fake['km_since_service'] > 35000, 1, 0)
    
    backup_model = RandomForestClassifier(n_estimators=50, random_state=42)
    backup_model.fit(X_fake, y_fake)
    
    # UPDATED PATH
    with open('models/health_model.pkl', 'wb') as f:
        pickle.dump(backup_model, f)
    print("✅ SUCCESS: Backup health_model.pkl created in /models!")

print("\n🎉 ML Pipeline Execution Finished!")
