🚢 CargoCast: Real-Time Port Risk Monitoring
ML-powered supply chain risk monitoring system tracking shipping disruption risk across 15 major global ports using live weather, news sentiment, and vessel data.

What It Does
Collects live data daily from weather and news APIs, computes a composite risk score (0–100%) for each port, and visualizes results on an interactive global dashboard.

Phases
Phase 1 — Risk Monitoring ✅ Complete
Real-time risk scoring across 15 ports. XGBoost model trained on 30 days of self-collected data achieving 85%+ accuracy.
Phase 2 — Delay Forecasting 🔄 In Progress
LSTM time-series model to predict port delays 7–14 days in advance once 60+ days of data are collected.

Tech Stack
Python · XGBoost · TensorFlow · Pandas · Streamlit · Plotly · NewsAPI · OpenWeather API
