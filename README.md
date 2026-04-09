# ⛽ PetroPulse AI: Fleet Command Center

![PetroPulse Header](https://img.shields.io/badge/Status-Hackathon_Ready-success) ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B) ![Gemini](https://img.shields.io/badge/AI-Google_Gemini-orange)

## 💻 Installation & Local Setup

1. **Clone the repository**
   ```bash
   git clone [https://github.com/YourUsername/PetroPulse-AI.git](https://github.com/YourUsername/PetroPulse-AI.git)
   cd PetroPulse-AI
2. **Streamlit URL:** https://petropulseai-bvmp5dnm97mdjfsomuqkst.streamlit.app/

## ABOUT
PetroPulse AI is an intelligent logistics dashboard built to solve the two biggest profit-killers in the Indian transport industry: **fuel price volatility** and **empty return miles (deadhead)**.

By combining real-time global market data, custom Machine Learning models, and an autonomous AI Orchestrator, PetroPulse transforms static fleet data into actionable, profit-generating strategies.

## 🚀 Core Features

* **🗺️ Spatial Route Arbitrage:** A 2D interactive radar that tracks fleet routes and identifies state-border VAT differences, dropping "Gold Pins" on optimal refill stations to save ₹2-3 per liter.
* **🤖 FastMCP AI Co-Pilot:** Powered by Google Gemini 2.5 Flash, our conversational agent has direct access to live weather, market volatility, and your specific fleet parameters to act as a 24/7 financial advisor.
* **📈 Predictive ML Forecaster:** Uses `scikit-learn` Random Forest models trained on historical logistics data to accurately predict fuel consumption and vehicle breakdown risks.
* **🔄 Backhaul Load Matcher:** A live scanner that identifies trucks returning empty and matches them with priority freight to turn a loss-making return journey into a profitable one.
* **🌍 Live Context Engine:** Pulls real-time Brent Crude futures via `yfinance` and live route weather via `Open-Meteo` to adjust ETAs and financial projections instantly.

## 🛠️ Tech Stack

* **Frontend:** Streamlit, Plotly, PyDeck (CartoDB Maps)
* **Backend / AI:** Python, Google Gemini API, FastMCP Server
* **Machine Learning:** Scikit-Learn, Pandas, NumPy
* **Live Data Integration:** YFinance (Market), Requests (Weather API)


