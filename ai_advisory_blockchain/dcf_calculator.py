import numpy as np
import pandas as pd
import stock_universe

dcf_assumptions = {
    "pre_tax_cost_of_debt": 0.085,
    "tax_rate": 0.25,
    "weight_equity": 0.75,
    "weight_debt": 0.25,
    "terminal_growth": 0.05
}
EBIT_assumptions = {
    "year1": {"EBITDA": 1000000, "DEP": 35000, "CAPEX": 55000, "NWC_change": 20000},   
    "year2": {"EBITDA": 1100000, "DEP": 38500, "CAPEX": 60500, "NWC_change": -2000},
    "year3": {"EBITDA": 1050000, "DEP": 40750, "CAPEX": 57750, "NWC_change": 11000},
    "year4": {"EBITDA": 1180000, "DEP": 43000, "CAPEX": 64900, "NWC_change": 25000},
    "year5": {"EBITDA": 1350000, "DEP": 47000, "CAPEX": 74250, "NWC_change": 27000}
}
EV_EBITDA_MULTIPLIER = {"PAYFIN": 10.0, "PAYRETAIL": 8.0, "PAYINFRA": 9.0, "PAYGOLD": 7.0, "PAYBOND": 6.0, "PAYTECH": 11.0}

def get_stock_data(ticker: str):
  return stock_universe.STOCK_UNIVERSE.get(ticker), stock_universe.MARKET_RETURN, stock_universe.RISK_FREE_RATE

def calculate_fcff(year: str):
    ebitda = EBIT_assumptions.get(year).get("EBITDA")
    dep = EBIT_assumptions.get(year).get("DEP")
    capex = EBIT_assumptions.get(year).get("CAPEX")
    nwc_change = EBIT_assumptions.get(year).get("NWC_change")
    ebit = ebitda - dep
    tax_rate = dcf_assumptions.get("tax_rate")
    fcff = ebit * (1 - tax_rate) + dep - capex - nwc_change
    return fcff

def calculate_wacc(ticker: str):
    stock_data, market_return, risk_free_rate = get_stock_data(ticker)
    beta = stock_data.get("beta")
    cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
    after_tax_cost_of_debt = dcf_assumptions.get("pre_tax_cost_of_debt") * (1 - dcf_assumptions.get("tax_rate"))
    weight_equity = dcf_assumptions.get("weight_equity")
    weight_debt = dcf_assumptions.get("weight_debt") 
    wacc = (weight_equity * cost_of_equity) + (weight_debt * after_tax_cost_of_debt)
    print(f"WACC for {ticker}: {wacc:.4f}")
    return wacc

def calculate_terminal_value(fcff_year5: float, wacc: float, terminal_growth: float):
    if terminal_growth is None:
        terminal_growth = dcf_assumptions.get("terminal_growth")
    terminal_value = fcff_year5 * (1 + terminal_growth) / (wacc - terminal_growth)
    return terminal_value

def calculate_dcf(ticker: str, wacc: float, terminal_growth: float):
    if wacc is None:
        wacc = calculate_wacc(ticker)
    if terminal_growth is None:
        terminal_growth = dcf_assumptions.get("terminal_growth")
    
    fcff_values = []
    for year in ["year1", "year2", "year3", "year4", "year5"]:
        fcff = calculate_fcff(year)
        fcff_values.append(fcff)
    #print(f"FCFF values for {ticker}: {fcff_values}")
    
    terminal_value = calculate_terminal_value(fcff_values[-1], wacc, terminal_growth)
    #print(f"Terminal Value for {ticker}: {terminal_value:.2f}")
    discounted_fcffs = [fcff / ((1 + wacc) ** (i + 1)) for i, fcff in enumerate(fcff_values)]
    discounted_terminal_value = terminal_value / ((1 + wacc) ** 5)
    dcf_value = sum(discounted_fcffs) + discounted_terminal_value
    #print(f"DCF Value for {ticker}: {dcf_value:.2f}")
    return dcf_value

def generate_sensitivity_table_data(ticker: str):
    base_wacc = calculate_wacc(ticker)
    base_terminal_growth = dcf_assumptions.get("terminal_growth")
    
    sensitivity_table = {}
    for wacc_adjustment in [-0.01, 0, 0.01]:
        for terminal_growth_adjustment in [-0.01, 0, 0.01]:
            adjusted_wacc = base_wacc + wacc_adjustment
            adjusted_terminal_growth = base_terminal_growth + terminal_growth_adjustment
            dcf_value = calculate_dcf(ticker, wacc=adjusted_wacc, terminal_growth=adjusted_terminal_growth)
            sensitivity_table[(adjusted_wacc, adjusted_terminal_growth)] = dcf_value
    
    return pd.DataFrame.from_dict(sensitivity_table, orient='index', 
                                  columns=['DCF Value']).reset_index().rename(columns={'index': 'adjusted_wacc, adjusted_terminal_growth'})

#print(generate_sensitivity_table_data("PAYFIN").to_string())

# Print this in 3*3 table format with WACC as rows and terminal growth as columns, with the DCF value in each cell.
def print_sensitivity_table(sensitivity_df):
    wacc_values = sorted(sensitivity_df['adjusted_wacc, adjusted_terminal_growth'].apply(lambda x: x[0]).unique())
    terminal_growth_values = sorted(sensitivity_df['adjusted_wacc, adjusted_terminal_growth'].apply(lambda x: x[1]).unique())
    
    table = pd.DataFrame(index=wacc_values, columns=terminal_growth_values)
    
    for _, row in sensitivity_df.iterrows():
        wacc, terminal_growth = row['adjusted_wacc, adjusted_terminal_growth']
        table.at[wacc, terminal_growth] = round(row['DCF Value'], 2)
    
    print(table)

def compare_EVEBITDA_DCF(ticker: str):
    ebitda_year5 = EBIT_assumptions.get("year5").get("EBITDA")
    ev_ebitda_value = ebitda_year5 * EV_EBITDA_MULTIPLIER.get(ticker)
    dcf_value = calculate_dcf(ticker, wacc=None, terminal_growth=None)
    
    comparison_df = pd.DataFrame({
        'Method': ['EV/EBITDA', 'DCF'],
        'Value (Rs)': [ev_ebitda_value, round(dcf_value, 2)]
    })
    
    return comparison_df

ticker = "PAYFIN"
print(f"DCF(Rs) for {ticker} under different WACC and terminal growth. Index Rows -> WACC, Index Columns -> Terminal Growth")
print_sensitivity_table(generate_sensitivity_table_data(ticker))


print(f"\nComparison of EV/EBITDA and DCF for {ticker}:")
print(compare_EVEBITDA_DCF(ticker).to_string(index=False))