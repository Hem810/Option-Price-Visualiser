import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# First, let's create the Black-Scholes module
class BlackScholes:
    def __init__(self, S, K, T, r, sigma, q=0):
        """
        Initialize Black-Scholes model parameters
        S: spot price
        K: strike price
        T: time to maturity (in years)
        r: risk-free rate
        sigma: volatility
        q: dividend yield (default 0)
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.q = q
        
        # Calculate d1 and d2
        self.d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        self.d2 = self.d1 - sigma * np.sqrt(T)
    
    def call_price(self):
        """Calculate call option price"""
        return (self.S * np.exp(-self.q * self.T) * norm.cdf(self.d1) - 
                self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2))
    
    def put_price(self):
        """Calculate put option price"""
        return (self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2) - 
                self.S * np.exp(-self.q * self.T) * norm.cdf(-self.d1))
    
    def delta(self, option_type='call'):
        """Calculate Delta"""
        if option_type == 'call':
            return np.exp(-self.q * self.T) * norm.cdf(self.d1)
        else:
            return np.exp(-self.q * self.T) * (norm.cdf(self.d1) - 1)
    
    def gamma(self):
        """Calculate Gamma"""
        return (np.exp(-self.q * self.T) * norm.pdf(self.d1)) / (self.S * self.sigma * np.sqrt(self.T))
    
    def vega(self):
        """Calculate Vega"""
        return self.S * np.exp(-self.q * self.T) * norm.pdf(self.d1) * np.sqrt(self.T) / 100
    
    def theta(self, option_type='call'):
        """Calculate Theta"""
        term1 = -(self.S * np.exp(-self.q * self.T) * norm.pdf(self.d1) * self.sigma) / (2 * np.sqrt(self.T))
        term2 = self.q * self.S * np.exp(-self.q * self.T) * norm.cdf(self.d1 if option_type=='call' else -self.d1)
        term3 = self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2 if option_type=='call' else -self.d2)
        
        if option_type == 'call':
            return (term1 - term2 - term3) / 365
        else:
            return (term1 + term2 + term3) / 365
    
    def rho(self, option_type='call'):
        """Calculate Rho"""
        if option_type == 'call':
            return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2) / 100
        else:
            return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2) / 100

# Test the Black-Scholes implementation
bs = BlackScholes(S=100, K=100, T=1, r=0.05, sigma=0.2)
print("Black-Scholes Model Test:")
print(f"Call Price: ${bs.call_price():.2f}")
print(f"Put Price: ${bs.put_price():.2f}")
print(f"Call Delta: {bs.delta('call'):.4f}")
print(f"Put Delta: {bs.delta('put'):.4f}")
print(f"Gamma: {bs.gamma():.4f}")
print(f"Vega: {bs.vega():.4f}")
print(f"Call Theta: {bs.theta('call'):.4f}")
print(f"Put Theta: {bs.theta('put'):.4f}")
print(f"Call Rho: {bs.rho('call'):.4f}")
print(f"Put Rho: {bs.rho('put'):.4f}")