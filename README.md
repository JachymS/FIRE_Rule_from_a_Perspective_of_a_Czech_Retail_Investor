# FIRE Rule from a Perspective of a Czech Retail Investor
This repository serves as a storage for code, requirements and seeds used during analysis used for Bachelor's thesis FIRE Rule From a Perspective of a Czech Retail Investor, Svejda (2025), advisor Mgr. Petr Polák, M.Sc., Ph.D. The thesis was defended on 10 June 2025.

## Thesis Text
*   [thesis.pdf](./thesis.pdf): Full text in the repository.
*   [Charles University Digital Repository](https://dspace.cuni.cz/handle/20.500.11956/199737): Official version.

## Repository Structure
*   `thesis.pdf`: Thesis text.
*   `Monte_Carlo/`: Simulation scripts.
*   `Visualizations/`: Graphs and plots.
*   `data/`: Input datasets (returns, FX, inflation).
*   `processing/`: Data cleaning and processing scripts.
*   `requirements.txt`: Python dependencies.

## Abstract
The thesis estimates a safe withdrawal rate for a Czech retail investor interested in the Financial Independence, Retire Early (FIRE) movement. It is assumed the investor aims for a 30–year payout period and their portfolio is active in up to three markets: the Czech Republic, the Eurozone, and the US. The market considerations are divided into four scenarios, representing different allocations of funds across the markets. Furthermore, the thesis assumes a fixed construction of the portfolio in assets to be an equal combination of stocks and bonds. The estimation is approached through a Monte Carlo Simulation that generates annual logarithmic returns of the assets and the exchange rates when applicable, while employing Cholesky decomposition to capture the empirical correlation among the variables. Inflation is modelled independently, and different treatments are applied depending on whether the investor owns a property. In total, seven different withdrawal rates are investigated, and it is concluded the safe withdrawal rate, or the FIRE rule, is 2.5% for the Czech investor in most of the scenarios considered, but can rise to 3% with international diversification and own housing.


## Bibliographic Record
Svejda, Jachym: FIRE Rule From a Perspective of a Czech Retail Investor. Bachelor’s thesis. Charles University, Faculty of Social Sciences, Institute of Economic Studies, Prague. 2025, pages 64. Advisor: Mgr. Petr Polák, M.Sc., Ph.D.
