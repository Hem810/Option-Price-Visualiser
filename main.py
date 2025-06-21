import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date,timedelta
import yfinance as yf
from models import BlackScholes as B
from models import BinomialTree as BT
from models import ImpliedVolatility as IV
from plots import utility

st.set_page_config(page_title="Options Pricing Visualizer", layout="wide")

with st.sidebar:
    st.header("Model Parameters")
    model_type = st.selectbox("Pricing Model", ["Black-Scholes", "Binomial Tree"])
    option_type = st.selectbox("Option Type", ["Call", "Put"])
    exercise_type = st.selectbox("Exercise Style", ["European", "American"]) if model_type == "Binomial Tree" else "European"
    
    col1, col2 = st.columns(2)
    with col1:
        S = st.number_input("Spot Price (S)", 50.0, 500.0, 100.0)
        K = st.number_input("Strike Price (K)", 50.0, 500.0, 100.0)
        r = st.number_input("Risk-Free Rate (%)", 0.0, 15.0, 5.0) / 100
    with col2:
        T = st.number_input("Time to Maturity (Years)", 0.1, 5.0, 1.0)
        sigma = st.number_input("Volatility (σ)", 0.01, 2.0, 0.2)
        q = st.number_input("Dividend Yield (%)", 0.0, 10.0, 0.0) / 100
    
    if model_type == "Binomial Tree":
        n_steps = st.slider("Tree Steps", 10, 500, 100)

tab1, tab2, tab3, tab4 = st.tabs(["Pricing Models", "Greeks Calculator", "Market Data", "IV Surface"])

with tab1:     # Pricing Models
    st.header("Option Pricing Comparison")
    
    
    bs_price = B.BlackScholes(S, K, T, r, sigma, q).call_price() if option_type == "Call" else B.BlackScholes(S, K, T, r, sigma, q).put_price()
    
    if model_type == "Binomial Tree":
        bt = BT.BinomialTree(S, K, T, r, sigma, n_steps, q, 
                         option_type.lower(), exercise_type.lower())
        tree_price = bt.price()
    
    cols = st.columns(3)
    with cols[0]:
        st.metric("Black-Scholes Price", f"${bs_price:.2f}")
    if model_type == "Binomial Tree":
        with cols[1]:
            st.metric(f"Binomial {exercise_type} Price", f"${tree_price:.2f}")
        with cols[2]:
            diff = bs_price - tree_price
            st.metric("Difference", f"${diff:.4f}", delta_color="off")

    st.subheader("Price Sensitivity Analysis")
    vol_range = np.linspace(0.1, 0.8, 50)
    strikes = np.linspace(S*0.5, S*1.5, 50)
    X, Y = np.meshgrid(strikes, vol_range)
    
    prices = np.zeros_like(X)
    for i in range(len(vol_range)):
        for j in range(len(strikes)):
            bs = B.BlackScholes(S, X[i,j], T, r, Y[i,j], q)
            prices[i,j] = bs.call_price() if option_type == "Call" else bs.put_price()
    
    fig = go.Figure(data=[go.Surface(x=X, y=Y, z=prices)])
    fig.update_layout(scene=dict(
        xaxis_title='Strike Price',
        yaxis_title='Volatility',
        zaxis_title='Option Price'),
        height=800
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:  # Greeks Calculator
    st.header("Option Greeks Analysis")
    
    bs = B.BlackScholes(S, K, T, r, sigma, q)
    greeks = {
        'Delta': bs.delta(option_type.lower()),
        'Gamma': bs.gamma(),
        'Vega': bs.vega(),
        'Theta': bs.theta(option_type.lower()),
        'Rho': bs.rho(option_type.lower())
    }
    
    # Display in table
    st.dataframe(
        pd.DataFrame.from_dict(greeks, orient='index', columns=['Value']).T,
        use_container_width=True
    )
    
    # Visualize Greeks sensitivity
    st.subheader("Dynamic Greeks Visualization")
    param = st.selectbox("Vary Parameter", ["Volatility", "Time to Maturity"])
    
    if param == "Volatility":
        x = np.linspace(0.1, 0.8, 50)
        y = [B.BlackScholes(S, K, T, r, vol, q).delta(option_type.lower()) for vol in x]
    else:
        x = np.linspace(0.1, T, 50)
        y = [B.BlackScholes(S, K, t, r, sigma, q).delta(option_type.lower()) for t in x]
    
    fig = px.line(x=x, y=y, labels={'x': param, 'y': 'Delta'})
    st.plotly_chart(fig, use_container_width=True)

with tab3:  # Market Data
    st.header("Real Market Data Comparison")
    ticker_s=st.text_input("Enter Ticker Symbol", "AAPL")
    ticker = yf.Ticker("AAPL") 
    expirations = ticker.options
    if not expirations:
        st.error("No option expiration dates available for this ticker.")
    else:
        selected_expiry = st.selectbox("Select Expiration Date", expirations)

        st.write(f"You selected: {selected_expiry}")
    chain=ticker.option_chain(selected_expiry)
    option_type = st.selectbox("Call/Put option", ["Call", "Put"])
    try:
        options = chain.calls if option_type == "Call" else chain.puts
        S = ticker.info['regularMarketPrice']
        # Calculate theoretical prices
        options['Theoretical'] = options.apply(lambda row: 
            B.BlackScholes(S, row['strike'], T, r, sigma, q).call_price()
            if option_type == "Call" else
            B.BlackScholes(S, row['strike'], T, r, sigma, q).put_price(), axis=1)
        
        # Display comparison
        st.write(f"Spot Price:{S}")
        st.dataframe(options[['strike', 'lastPrice', 'Theoretical', 'impliedVolatility']], 
                    use_container_width=True)
        
    except Exception as e:
        st.error(f"Error fetching market data: {str(e)}")

with tab4:  # IV Surface
    st.header("Implied Volatility Analysis")
    
    market_price = st.number_input("Market Price", 0.01, 1000.0, bs_price)
    iv_calculator = IV.ImpliedVolatility(S, K, T, r, market_price, option_type.lower(), q)
    iv = iv_calculator.calculate_iv()
    
    cols = st.columns(2)
    with cols[0]:
        if(iv):
            st.metric("Calculated IV", f"{int(iv*100)/100}")
        else:
            st.metric("Calculated IV", 0)
            iv=0
    with cols[1]:
        st.metric("BS Price with IV", f"${int(B.BlackScholes(S, K, T, r, iv, q).call_price()*100)/100}")
    
    # IV Surface visualization
    st.subheader("3D IV Surface")
    strikes = np.linspace(S*0.7, S*1.3, 20)
    expiries = np.linspace(0.1, 2.0, 20)
    
    iv_grid = np.zeros((len(expiries), len(strikes)))
    for i, T_iv in enumerate(expiries):
        for j, K_iv in enumerate(strikes):
            iv_calc = IV.ImpliedVolatility(S, K_iv, T_iv, r, market_price, option_type.lower(), q)
            iv_grid[i,j] = iv_calc.calculate_iv()
    
    fig = go.Figure(data=[go.Surface(x=strikes, y=expiries, z=iv_grid)])
    fig.update_layout(scene=dict(
        xaxis_title='Strike Price',
        yaxis_title='Time to Expiry',
        zaxis_title='Implied Volatility'),
        height=800
    )
    st.plotly_chart(fig, use_container_width=True)
