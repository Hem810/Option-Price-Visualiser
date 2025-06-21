# Create the Implied Volatility module
from models import BlackScholes as b
from scipy.optimize import brentq
import pandas as pd
class ImpliedVolatility:
    def __init__(self, S, K, T, r, market_price, option_type='call', q=0):
        """
        Initialize Implied Volatility calculator
        S: spot price
        K: strike price
        T: time to maturity
        r: risk-free rate
        market_price: observed market price
        option_type: 'call' or 'put'
        q: dividend yield
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.market_price = market_price
        self.option_type = option_type
        self.q = q
    
    def calculate_iv(self, method='brentq'):
        """Calculate implied volatility using numerical methods"""
        def objective(sigma):
            bs = b.BlackScholes(self.S, self.K, self.T, self.r, sigma, self.q)
            if self.option_type == 'call':
                theoretical_price = bs.call_price()
            else:
                theoretical_price = bs.put_price()
            return theoretical_price - self.market_price
        
        try:
            # Use Brent's method to find the root
            iv = brentq(objective, 0.001, 5.0)
            return iv
        except ValueError:
            # If Brent's method fails, try a different approach
            return None
    
    def vega_newton(self, sigma_initial=0.2, max_iterations=100, tolerance=1e-6):
        """Calculate IV using Newton-Raphson method with Vega"""
        sigma = sigma_initial
        
        for i in range(max_iterations):
            bs = b.BlackScholes(self.S, self.K, self.T, self.r, sigma, self.q)
            
            if self.option_type == 'call':
                price = bs.call_price()
            else:
                price = bs.put_price()
            
            vega = bs.vega() * 100  # Convert back from percentage
            
            price_diff = price - self.market_price
            
            if abs(price_diff) < tolerance:
                return sigma
            
            if vega == 0:
                break
                
            sigma = sigma - price_diff / vega
            
            # Keep sigma positive
            if sigma <= 0:
                sigma = 0.001
        
        return sigma

# Test the Implied Volatility calculator
print("\nImplied Volatility Test:")

# Create a market price using known volatility
test_sigma = 0.25
bs_test = b.BlackScholes(S=100, K=100, T=1, r=0.05, sigma=test_sigma)
market_call_price = bs_test.call_price()
market_put_price = bs_test.put_price()

print(f"Original volatility: {test_sigma:.3f}")
print(f"Market call price: ${market_call_price:.2f}")
print(f"Market put price: ${market_put_price:.2f}")

# Calculate implied volatility
iv_calc_call = ImpliedVolatility(S=100, K=100, T=1, r=0.05, market_price=market_call_price, option_type='call')
iv_calc_put = ImpliedVolatility(S=100, K=100, T=1, r=0.05, market_price=market_put_price, option_type='put')

iv_call = iv_calc_call.calculate_iv()
iv_put = iv_calc_put.calculate_iv()

print(f"Implied volatility (call): {iv_call:.3f}")
print(f"Implied volatility (put): {iv_put:.3f}")

# Test Newton-Raphson method
iv_call_newton = iv_calc_call.vega_newton()
iv_put_newton = iv_calc_put.vega_newton()

print(f"IV using Newton-Raphson (call): {iv_call_newton:.3f}")
print(f"IV using Newton-Raphson (put): {iv_put_newton:.3f}")

# Test with different strikes to create IV surface data
strikes = [90, 95, 100, 105, 110]
iv_surface_data = []

print("\nIV Surface Data:")
for K in strikes:
    bs_surface = b.BlackScholes(S=100, K=K, T=1, r=0.05, sigma=0.2)
    market_price = bs_surface.call_price()
    iv_calc = ImpliedVolatility(S=100, K=K, T=1, r=0.05, market_price=market_price, option_type='call')
    iv = iv_calc.calculate_iv()
    iv_surface_data.append({'Strike': K, 'Market_Price': market_price, 'IV': iv})
    print(f"Strike {K}: Market Price ${market_price:.2f}, IV {iv:.3f}")

# Convert to DataFrame for easier handling
iv_df = pd.DataFrame(iv_surface_data)
print("\nIV Surface DataFrame:")
print(iv_df)