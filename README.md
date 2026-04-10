<div align="center">
  
# ⛽ PetroPulse AI by Team- Chai-patti
**The Next-Generation Fleet Command Center for Indian Logistics**

[![Status](https://img.shields.io/badge/Status-Production_Ready-00FFCC?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)]()
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)]()
[![Gemini](https://img.shields.io/badge/AI-Gemini_2.5_Flash-orange?style=for-the-badge&logo=google&logoColor=white)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)]()

*Transforming static fleet data into real-time, profit-generating operational strategies.*

</div>



## 🚀 The Problem vs. The Solution

The Indian logistics sector is the backbone of India's entire economy but this same industry loses billions annually to a few silent killers common to every Industry that are **Fuel Price Volatility** and **DeadheadReturn Miles**. 

**PetroPulse AI** solves this by acting as an autonomous, multi-agent financial advisor. By combining live global market feeds, custom Machine Learning models, and spatial state-tax arbitrage, PetroPulse ensures that every route driven is mathematically optimized for maximum profit to these companies which are the real backbone.


## ✨ Core Features

* ** Spatial Route Arbitrage (Auto-Zooming Maps)**
  * Powered by `PyDeck` and `CartoDB`, our interactive 2D map dynamically auto-centers on active fleet routes.
  * Drops precise "Gold Pins" on optimal state-border refueling depots, visualizing exact VAT savings (e.g., Save ₹2.62/L at Haryana Border).
* ** FastMCP AI Co-Pilot**
  * A state-of-the-art Google Gemini 2.5 Flash agent equipped with **Smart Approximation Protocol**.
  * Reads live dashboard state (weather, Brent Crude prices, fleet size) to provide real-time, mathematically grounded financial consulting.
* ** Predictive ML Forecaster**
  * Custom `scikit-learn` Random Forest algorithms trained on historical logistics data.
  * Accurately predicts exact fuel consumption and calculates fleet breakdown risks based on load weight and service history.
* ** Backhaul Load Matcher**
  * A live radar that identifies trucks returning empty and matches them with priority freight, turning the old loss-making return journey into instant revenue.
* **Live Context Engine**
  * Synthesizes live Brent Crude futures (`yfinance`) and real-time route weather (`Open-Meteo`) to adjust ETAs and financial projections instantly.

---

## 🔍 Code Spotlight: Dynamic Context Injection

PetroPulse AI doesn't just use a generic chatbot. We engineered a dynamic context pipeline that intercepts the live UI state (weather, crude prices, slider values) and hardwires it into the LLM's system instructions. This turns a standard LLM into an **Agentic Orchestrator**.

```python
# 🧠 Dynamic Context Injection Pipeline
system_context = f"""
You are PetroPulse AI, an elite logistics financial advisor for India. 

CURRENT DASHBOARD CONTEXT:
- Active Route: {route_select} (Distance: {current_route['distance']} km).
- Fleet: {fleet_size} trucks averaging {avg_mileage} kmpl.
- Arbitrage Savings: ₹{price_diff:.2f}/L at {current_route['border_state']} border.
- Live Brent Crude: ${brent_val:.2f}. USD/INR: ₹{inr_val:.2f}.
- Live Weather: Origin({o_cond}), Dest({d_cond}).

CRITICAL INSTRUCTION:
Act as a senior logistics consultant. Use the exact mathematical metrics provided above to calculate costs and savings for the user in real-time.
"""

# Initialize the Gemini Model with real-time UI state
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction=system_context
)
```

## 🛠️ Technology Stack

| Category | Technologies Used |
| :--- | :--- |
| **Frontend UI** | Streamlit, Plotly Graph Objects, PyDeck (CartoDB) |
| **Backend & AI** | Python, Google Gemini API, FastMCP (Model Context Protocol) |
| **Machine Learning** | Scikit-Learn, Pandas, NumPy, Pickle |
| **Live Data APIs** | YFinance (Global Markets), Open-Meteo (Meteorological Data) |

---

## 🏗️ System Architecture

We adhere to strict separation of concerns, isolating our raw data, machine learning models, and application logic into a production-grade directory structure.

```text
PetroPulse_AI/
├── data/                      #  Raw logistics datasets (Routes & Health)
├── models/                    # Compiled Random Forest .pkl brains
├── app.py                     #  Main Streamlit UI & Dashboard
├── server.py                  #  FastMCP AI Orchestrator
├── train_models.py            # ML Training Pipeline
├── requirements.txt           #  Dependency management
└── .env                       #  Environment variables (Git-Ignored)
```

---

## 💻 Local Installation & Setup

Want to run PetroPulse AI locally? Follow these steps:

**1. Clone the repository**
```bash
git clone [https://github.com/DevSolanki-works/PetroPulse_AI.git](https://github.com/DevSolanki-works/PetroPulse_AI.git)
cd PetroPulse_AI
```

**2. Create and activate a Virtual Environment**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up your Environment Variables**
Create a `.env` file in the root directory and add your Gemini API Key:
```env
GEMINI_API_KEY="your_api_key_here"
```

**5. Train the Machine Learning Models**
*(Required for first-time setup to generate the `.pkl` files)*
```bash
python train_models.py
```

**6. Launch the App!**
```bash
streamlit run app.py
```

---

## 💡 Hackathon Notes
This project was conceived, designed, and deployed within a strict 24-hour hackathon timeframe. 
* The Machine Learning models are custom-trained on synthesized datasets representing real-world Indian logistics conditions.
* The API integrations (YFinance and Open-Meteo) are 100% live and fetching real-time data.
* We completely bypassed traditional web-scraping for fuel prices by mapping global Brent Crude volatility directly to local OMC spot prices.

---
<div align="center">
  <b>Built with ❤️ and ☕ for the Hackathon Finals.</b>
</div>
