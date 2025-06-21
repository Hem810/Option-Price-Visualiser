import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
import matplotlib.pyplot as plt
from models import BlackScholes as b

class BinomialTree:
    def __init__(self, S, K, T, r, sigma, n=100, q=0, option_type='call', exercise_type='european'):
        """
        Initialize Binomial Tree model parameters
        S: spot price
        K: strike price
        T: time to maturity (in years)
        r: risk-free rate
        sigma: volatility
        n: number of time steps
        q: dividend yield (default 0)
        option_type: 'call' or 'put'
        exercise_type: 'european' or 'american'
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.n = n
        self.q = q
        self.option_type = option_type
        self.exercise_type = exercise_type
        
        # Calculate tree parameters
        self.dt = T / n
        self.u = np.exp(sigma * np.sqrt(self.dt))  # up factor
        self.d = 1 / self.u  # down factor
        self.p = (np.exp((r - q) * self.dt) - self.d) / (self.u - self.d)  # risk-neutral probability
        self.discount = np.exp(-r * self.dt)
    
    def price(self):
        """Calculate option price using binomial tree"""
        # Initialize asset prices at maturity
        S_T = np.zeros(self.n + 1)
        for i in range(self.n + 1):
            S_T[i] = self.S * (self.u ** (self.n - i)) * (self.d ** i)
        
        # Initialize option values at maturity
        V = np.zeros(self.n + 1)
        for i in range(self.n + 1):
            if self.option_type == 'call':
                V[i] = max(0, S_T[i] - self.K)
            else:
                V[i] = max(0, self.K - S_T[i])
        
        # Backward induction
        for j in range(self.n - 1, -1, -1):
            for i in range(j + 1):
                # Calculate continuation value
                V[i] = self.discount * (self.p * V[i] + (1 - self.p) * V[i + 1])
                
                # For American options, check early exercise
                if self.exercise_type == 'american':
                    S_now = self.S * (self.u ** (j - i)) * (self.d ** i)
                    if self.option_type == 'call':
                        exercise_value = max(0, S_now - self.K)
                    else:
                        exercise_value = max(0, self.K - S_now)
                    V[i] = max(V[i], exercise_value)
        
        return V[0]
    
    def get_tree_data(self):
        """Get the complete tree data for visualization"""
        # Create price tree
        price_tree = np.zeros((self.n + 1, self.n + 1))
        for j in range(self.n + 1):
            for i in range(j + 1):
                price_tree[i, j] = self.S * (self.u ** (j - i)) * (self.d ** i)
        
        return price_tree

# Test the Binomial Tree implementation
bs = b.BlackScholes(S=100, K=100, T=1, r=0.05, sigma=0.2)
bt_european = BinomialTree(S=100, K=100, T=1, r=0.05, sigma=0.2, n=100, option_type='call', exercise_type='european')
bt_american = BinomialTree(S=100, K=100, T=1, r=0.05, sigma=0.2, n=100, option_type='call', exercise_type='american')

print("\nBinomial Tree Model Test:")
print(f"European Call Price: ${bt_european.price():.2f}")
print(f"American Call Price: ${bt_american.price():.2f}")

# Compare with Black-Scholes
bs_call = bs.call_price()
print(f"Black-Scholes Call Price: ${bs_call:.2f}")
print(f"Binomial vs BS difference: ${bt_european.price() - bs_call:.2f}")

# Test for put options
bt_put_european = BinomialTree(S=100, K=100, T=1, r=0.05, sigma=0.2, n=100, option_type='put', exercise_type='european')
bt_put_american = BinomialTree(S=100, K=100, T=1, r=0.05, sigma=0.2, n=100, option_type='put', exercise_type='american')

print(f"\nEuropean Put Price: ${bt_put_european.price():.2f}")
print(f"American Put Price: ${bt_put_american.price():.2f}")
print(f"Black-Scholes Put Price: ${bs.put_price():.2f}")