"""Code used for Monte Carlo Simulation"""

# Import of necessary packages
import numpy as np
import scipy.stats as st
import json

# Functions used in MCS with cholesky decomposition
def load_statistics():
    """ Loads json file. """
    with open("/Users/jachymsvejda/Documents/GitHub/FIRE_Rule_from_a_Perspective_of_a_Czech_Retail_Investor/data/relationships/statistics.json") as f:
        return json.load(f)
def inflation(dictionary,housing=False):
    """ Generates inflation lower than 50% from specified lognormal distribution. """
    mu = dictionary["Infl_log_total_mean"]
    sigma = dictionary["Infl_log_total_std"]
    # Calculate upper bound (50%) in standard normal units:
    b = (np.log(0.5) - mu) / sigma
    # Return Inflation
    out=np.exp(st.truncnorm.rvs(a=-np.inf, b=b, loc=mu, scale=sigma))
    if housing:
        return  out - 0.001158 # underestimate inflation by housing
    return out
def cholesky_decomp(cz_market, eu_market, us_market):
    """ Loads Cholesky decomposition matrix for relevant markets. """
    if cz_market==1:
        return np.load("/Users/jachymsvejda/Documents/GitHub/FIRE_Rule_from_a_Perspective_of_a_Czech_Retail_Investor/data/relationships/cholesky_decomposition_cz.npy")
    elif cz_market==0:
        return np.load("/Users/jachymsvejda/Documents/GitHub/FIRE_Rule_from_a_Perspective_of_a_Czech_Retail_Investor/data/relationships/cholesky_decomposition_foreign.npy")
    return np.load("/Users/jachymsvejda/Documents/GitHub/FIRE_Rule_from_a_Perspective_of_a_Czech_Retail_Investor/data/relationships/cholesky_decomposition_all.npy")
def simulation(means, L):
    """ Simulates correlated returns. """
    z = np.random.normal(0, 1, len(means))
    return means + L @ z
def asset_split(value, share):
    """ Splits appropriate share of initial value to stocks and bonds equally. """
    return (value * share)/2, (value * share)/2

# Actual MCS Simulation
def mcs(runs, withdrawal_rate, cz, eu, us, house=False, debugging=False):
    """Monte Carlo Simulation.
        
        Arguments
        ----------------------
        runs : int
            number of runs
        withdrawal_rate : float
            initial withdrawal rate
        cz : float 
            share of portfolio allocated in the CZ market
        eu :
            share of portfolio allocated in the EU market
        us :
            share of portfolio allocated in the US market
        house: boolean (default: False)
            specifices whether inflation should be underestimated 
        debugging : boolean (default: False)
            returns additional info if True
        ----------------------
        
        Return
        ----------------------
        If debugging==False:
            portfolio_history : list
                portfolio value over every year and every simulation run
            withdrawal_history : list
                withdrawal value over every year and every simulation run
        If debugging==True:
            portfolio_history : list
                portfolio value over every year and every simulation run
            withdrawal_history : list
                withdrawal value over every year and every simulation run
            failed_runs : int
                number of simulations where portfolio did not last 30 years
            failed_portfolios : list
                final failed portfolio values
        """
    # Check input validity
    if debugging==False and (runs<=0 or (not (0<withdrawal_rate<=1)) or (cz+eu+us!=1)):
        raise Exception("Invalid arguments.")
    # Set seed
    np.random.seed(42)
    # Load statistics from json
    statistics = load_statistics()
    # Load Cholesky decomposition matrix
    cholesky = cholesky_decomp(cz_market=cz, eu_market=eu, us_market=us)
    # Define variables
    variables = ["PXTR", "CZBond"] if cz==1 else ["EUR", "USD", "SX5GT", "SPXTR", "DEBond", "USBond"] if cz==0 else ["EUR", "USD", "PXTR", "SX5GT", "SPXTR", "CZBond", "DEBond", "USBond"]
    # Define means of variables
    var_means = np.array([statistics[f"{a}_mean"] for a in variables])
    # Prepare array for results
    portfolio_history=[]
    withdrawal_history=[]
    real_portfolio_hist = []
    if debugging:
        failed_runs=0
        failed_portfolios=[]
    for _ in range(runs):
        # Initialize run details for logging
        if debugging:
            run_details = [] 
        # Set up for base year in every run
        year=0
        portfolio=15_000_000
        withdrawal_value=portfolio*withdrawal_rate
        price_index = 1
        # Intialize a list for yearly portfolio values
        yearly_port_values=[np.round(portfolio,2)]
        yearly_with_values=[np.round(withdrawal_value,2)]
        real_port_values=[np.round(portfolio/price_index,2)]
        # First year
        portfolio-=withdrawal_value
        yearly_port_values.append(np.round(portfolio,2))
        real_port_values.append(np.round(portfolio/price_index,2))
        cz_stock, cz_bond = asset_split(portfolio, cz)
        eu_stock, eu_bond = asset_split(portfolio, eu)
        us_stock, us_bond = asset_split(portfolio, us)
        year+=1
        # Loop over the rest of years or until portfolio is depleted
        while portfolio>0 and year<30:
            # Generate inflation
            infl = inflation(statistics, housing=house)
            # Append price index
            price_index*=(1 + infl)
            # Update iwv
            withdrawal_value*=(1+infl)
            yearly_with_values.append(np.round(withdrawal_value,2))
            # Generate returns 
            # + update on portfolio shares
            if cz==1:
                pxtr, czb = simulation(means=var_means, L=cholesky)
                cz=1
            elif cz==0:
                eur, usd, sx5gt, spxtr, eub, usb = simulation(means=var_means, L=cholesky)
                assets=np.sum([eu_stock,us_stock,eu_bond,us_bond])
                eu = np.sum([eu_stock, eu_bond]) / assets
                us = np.sum([us_stock, us_bond]) / assets 
            else:
                eur, usd, pxtr, sx5gt, spxtr, czb, eub, usb = simulation(means=var_means, L=cholesky)
                assets=np.sum([cz_stock,eu_stock,us_stock,cz_bond,eu_bond,us_bond])
                cz = np.sum([cz_stock, cz_bond]) / assets # perhaps add here np.round(...,4)
                eu = np.sum([eu_stock, eu_bond]) / assets # perhaps add here np.round(...,4)
                us = np.sum([us_stock, us_bond]) / assets # perhaps add here np.round(...,4)
            # Applying Returns
            if cz!=0:
                cz_stock *=  np.exp(pxtr) 
                cz_bond *= np.exp(czb) 
            if cz!=1: 
                # yearly application of exchange rate on assets because then it tracks the development of the foreign currency in time
                eu_stock *= np.exp(sx5gt+eur) 
                eu_bond *= np.exp(eub+eur) 
                us_stock *= np.exp(spxtr+usd) 
                us_bond *= np.exp(usb+usd) 
            # Withdrawal
            portfolio = np.sum([cz_stock,eu_stock,us_stock,cz_bond,eu_bond,us_bond])
            # Log details for this year
            if debugging:
                run_details.append({
                    'year': year + 1,
                    'portfolio': portfolio,
                    'withdrawal_value': withdrawal_value,
                    'inflation': infl,
                    'returns': {
                        'EUR': eur,
                        'USD': usd,
                        'PXTR': pxtr,
                        'SX5GT': sx5gt,
                        'SPXTR': spxtr,
                        'CZBond': czb,
                        'DEBond': eub,
                        'USBond': usb,
                    }
                })
            portfolio-=withdrawal_value
            # Rebalancing
            if portfolio>0:
                yearly_port_values.append(np.round(portfolio,2))
                real_port_values.append(np.round(portfolio / price_index,2))
                cz_stock, cz_bond = asset_split(portfolio, cz) #np.max([asset_split(portfolio, cz), 0])
                eu_stock, eu_bond = asset_split(portfolio, eu)#np.max([asset_split(portfolio, eu),0])
                us_stock, us_bond = asset_split(portfolio, us)#np.max([asset_split(portfolio, us),0])
                # Add a year
                year+=1
        # If this run ended with a depleted portfolio, log in the details
        if portfolio <= 0 and debugging:
            failed_portfolios.append(portfolio)
            for detail in run_details:
                print(detail)
            failed_runs+=1 if portfolio<=0 else 0
        #real_port_values = [yearly_port_values[t] / price_index[t] for t in range(len(yearly_port_values))] 
        real_portfolio_hist.append(real_port_values)      
        portfolio_history.append(yearly_port_values)
        withdrawal_history.append(yearly_with_values)
    if debugging:
        return portfolio_history, withdrawal_history, real_port_values, failed_runs, failed_portfolios
    return portfolio_history, withdrawal_history, real_portfolio_hist
