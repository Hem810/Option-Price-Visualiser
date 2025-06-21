# Option-Price-Visualiser
Using Black Scholes and Binomial Tree algorithm to determine and show option pricing 
Options Pricing Visualizer

A Python-based web application for visualizing and comparing option pricing models, Greeks, implied volatility, and real market data. Built with Streamlit for interactive data exploration.

Directory Structure:
.
├── main.py
├── models
│   ├── BinomialTree.py
│   ├── BlackScholes.py
│   └── ImpliedVolatility.py
└── plots
    └── utility.py

Features:
- Option Pricing Models: Compare the Black-Scholes model with the Binomial Tree model for both European and American options.
- Greeks Analysis: Visualize and calculate Greeks (Delta, Gamma, Vega, Theta, Rho) for selected options.
- Market Data Integration: Fetch and compare real option chain data from Yahoo Finance.
- Implied Volatility (IV) Analysis: Compute implied volatility from market prices and visualize IV surfaces.
- Interactive 3D Visualization: Explore how option prices and Greeks vary with spot price, strike, volatility, and time.

Installation:
1. Clone the repository:
   git clone https://github.com/yourusername/options-pricing-visualizer.git
   cd options-pricing-visualizer

2. Install dependencies:
   pip install -r requirements.txt

3. Run the application:
   streamlit run main.py

Usage:
- Model Selection: Choose between Black-Scholes and Binomial Tree models.
- Option Type & Exercise Style: Select call/put and European/American options.
- Parameter Input: Adjust spot price, strike, risk-free rate, volatility, dividend yield, and tree steps.
- Visualization Tabs:
  - Pricing Models: Compare model prices and visualize price sensitivity.
  - Greeks Calculator: View and visualize Greeks.
  - Market Data: Fetch and compare real option chain data.
  - IV Surface: Compute implied volatility and visualize IV surfaces.

License: MIT
