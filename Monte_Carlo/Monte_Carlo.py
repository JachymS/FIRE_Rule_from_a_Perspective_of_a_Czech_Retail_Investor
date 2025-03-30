# Code used for Monte Carlo Simulation

# Import of necessary packages
import numpy as np
import scipy.stats as st
import json

# Functions used in MCS with cholesky decomposition
def load_statistics():
    """ Loads json file. """
    with open("/Users/jachymsvejda/Documents/GitHub/FIRE_Rule_from_a_Perspective_of_a_Czech_Retail_Investor/data/relationships/statistics.json") as f:
        return json.load(f)
def inflation(dictionary):
    """ Generates inflation lower than 50% from specified lognormal distribution. """
    mu = dictionary["Infl_log_mean"]
    sigma = dictionary["Infl_log_std"]
    # Calculate upper bound (50%) in standard normal units:
    b = (np.log(0.5) - mu) / sigma
    # Return Inflation
    return np.exp(st.truncnorm.rvs(a=-np.inf, b=b, loc=mu, scale=sigma))
def cholesky_decomp():
    """ Loads Cholesky decomposition matrix. """
    return np.load("/Users/jachymsvejda/Documents/GitHub/FIRE_Rule_from_a_Perspective_of_a_Czech_Retail_Investor/data/relationships/cholesky_decomposition.npy")
def simulation(means, L):
    """ Simulates correlated returns. """
    z = np.random.normal(0, 1, len(means))
    return means + L @ z
def asset_split(value, share):
    """ Splits appropriate share of initial value to stocks and bonds equally. """
    return (value * share)/2, (value * share)/2

# Actual MCS Simulation
def mcs(runs, withdrawal_rate, cz, eu, us):
    """Monte Carlo Simulation.
        
        Arguments
        ----------------------
        runs = number of runs
        withdrawal_rate = initial withdrawal rate
        cz = share of portfolio allocated in the CZ market
        eu = share of portfolio allocated in the EU market
        us = share of portfolio allocated in the US market"""
    # Check input validity
    if runs<=0 or (not (0<withdrawal_rate<=1)) or (cz+eu+us!=1):
        raise Exception("Invalid arguments.")
    # Set seed
    np.random.seed(42)
    # Load statistics from json
    statistics = load_statistics()
    # Load Cholesky decomposition matrix
    cholesky = cholesky_decomp()
    # Define variables
    variables = ["EUR", "USD", "PXTR", "SX5GT", "SPXTR", "CZBond", "DEBond", "USBond"]
    # Define means of variables
    var_means = np.array([statistics[f"{a}_mean"] for a in variables])
    # Prepare array for results
    portfolio_history=[]
    withdrawal_history=[]
    for _ in range(runs):
        # Set up for base year in every run
        year=0
        portfolio=15_000_000
        withdrawal_value=portfolio*withdrawal_rate
        # Intialize a list for yearly portfolio values
        yearly_port_values=[np.round(portfolio,2)]
        yearly_with_values=[np.round(withdrawal_value,2)]
        # First year
        portfolio-=withdrawal_value
        cz_stock, cz_bond = asset_split(portfolio, cz)
        eu_stock, eu_bond = asset_split(portfolio, eu)
        us_stock, us_bond = asset_split(portfolio, us)
        # Loop over the rest of years or until portfolio is depleted
        while portfolio>0 and year<30:
            # Generate inflation
            infl = inflation(statistics)
            # Update iwv
            withdrawal_value*=(1+infl)
            yearly_with_values.append(np.round(withdrawal_value,2))
            # Generate returns 
            eur, usd, pxtr, sx5gt, spxtr, czb, eub, usb = simulation(means=var_means, L=cholesky)
            # Update on portfolio shares
            assets=np.sum([cz_stock,eu_stock,us_stock,cz_bond,eu_bond,us_bond])
            cz = np.sum([cz_stock, cz_bond]) / assets
            eu = np.sum([eu_stock, eu_bond]) / assets
            us = np.sum([us_stock, us_bond]) / assets
            # Applying Returns
            cz_stock *= (1+pxtr)
            cz_bond *= (1+czb)
            eu_stock *= (1+sx5gt)*(1+eur)
            eu_bond *= (1+eub)*(1+eur)
            us_stock *= (1+spxtr)*(1+usd)
            us_bond *= (1+usb)*(1+usd)
            # Withdrawal
            portfolio = np.sum([cz_stock,eu_stock,us_stock,cz_bond,eu_bond,us_bond])
            yearly_port_values.append(np.round(portfolio,2))
            portfolio-=withdrawal_value
            # Rebalancing
            cz_stock, cz_bond = asset_split(portfolio, cz)
            eu_stock, eu_bond = asset_split(portfolio, eu)
            us_stock, us_bond = asset_split(portfolio, us)
            # Add a year
            year+=1
        portfolio_history.append(yearly_port_values)
        withdrawal_history.append(yearly_with_values)
    return portfolio_history, withdrawal_history 
