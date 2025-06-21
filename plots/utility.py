import sys
from models import BlackScholes as b
import datetime as dt
import numpy as np
import pandas as pd

class OptionsUtils:
    @staticmethod
    def generate_3d_surface_data(S_range, vol_range, K, T, r, option_type='call'):
        """Generate 3D surface data for option price vs spot and volatility"""
        S_grid, vol_grid = np.meshgrid(S_range, vol_range)
        price_grid = np.zeros_like(S_grid)
        
        for i in range(len(vol_range)):
            for j in range(len(S_range)):
                bs = b.BlackScholes(S_grid[i,j], K, T, r, vol_grid[i,j])
                if option_type == 'call':
                    price_grid[i,j] = bs.call_price()
                else:
                    price_grid[i,j] = bs.put_price()
        
        return S_grid, vol_grid, price_grid
    
    @staticmethod
    def generate_greeks_data(S, K, T, r, sigma, q=0):
        """Generate comprehensive Greeks data"""
        bs = b.BlackScholes(S, K, T, r, sigma, q)
        
        greeks_data = {
            'Greek': ['Delta (Call)', 'Delta (Put)', 'Gamma', 'Vega', 'Theta (Call)', 'Theta (Put)', 'Rho (Call)', 'Rho (Put)'],
            'Value': [
                bs.delta('call'),
                bs.delta('put'),
                bs.gamma(),
                bs.vega(),
                bs.theta('call'),
                bs.theta('put'),
                bs.rho('call'),
                bs.rho('put')
            ],
            'Description': [
                'Rate of change in call option price with respect to underlying price',
                'Rate of change in put option price with respect to underlying price',
                'Rate of change in delta with respect to underlying price',
                'Rate of change in option price with respect to volatility (%)',
                'Rate of change in call option price with respect to time (per day)',
                'Rate of change in put option price with respect to time (per day)',
                'Rate of change in call option price with respect to interest rate (%)',
                'Rate of change in put option price with respect to interest rate (%)'
            ]
        }
        
        return pd.DataFrame(greeks_data)
    
    @staticmethod
    def time_to_maturity(expiry_date):
        """Calculate time to maturity in years"""
        if isinstance(expiry_date, str):
            expiry_date = dt.datetime.strptime(expiry_date, '%Y-%m-%d').date()
        elif isinstance(expiry_date, dt.datetime):
            expiry_date = expiry_date.date()
        
        today = dt.date.today()
        days_to_expiry = (expiry_date - today).days
        return max(days_to_expiry / 365.0, 0.001)  # Minimum 1 day to avoid division by zero
    
    @staticmethod
    def format_greeks_for_display(greeks_df):
        """Format Greeks data for better display"""
        formatted_df = greeks_df.copy()
        
        # Round values appropriately
        for i, greek in enumerate(formatted_df['Greek']):
            value = formatted_df.loc[i, 'Value']
            if 'Delta' in greek or 'Gamma' in greek:
                formatted_df.loc[i, 'Formatted_Value'] = f"{value:.4f}"
            elif 'Vega' in greek or 'Rho' in greek:
                formatted_df.loc[i, 'Formatted_Value'] = f"{value:.4f}"
            elif 'Theta' in greek:
                formatted_df.loc[i, 'Formatted_Value'] = f"{value:.6f}"
        
        return formatted_df

# Test the utility functions
print("Testing Utility Functions:")

# Test Greeks data generation
greeks_df = OptionsUtils.generate_greeks_data(S=100, K=100, T=1, r=0.05, sigma=0.2)
print("\nGreeks Data:")
print(greeks_df)

# Test formatted Greeks
formatted_greeks = OptionsUtils.format_greeks_for_display(greeks_df)
print("\nFormatted Greeks:")
print(formatted_greeks[['Greek', 'Formatted_Value']])

# Test time to maturity calculation
test_expiry = '2024-12-31'
ttm = OptionsUtils.time_to_maturity(test_expiry)
print(f"\nTime to maturity for {test_expiry}: {ttm:.3f} years")

# Test 3D surface data generation (small sample)
S_range = np.linspace(80, 120, 5)
vol_range = np.linspace(0.1, 0.4, 5)
S_grid, vol_grid, price_grid = OptionsUtils.generate_3d_surface_data(S_range, vol_range, K=100, T=1, r=0.05)

print("\n3D Surface Data Sample:")
print(f"Spot prices: {S_range}")
print(f"Volatilities: {vol_range}")
print(f"Price grid shape: {price_grid.shape}")
print(f"Sample prices: {price_grid[0, :]}")  # First row of prices