# Implement a 3-agent debate in debate.py for one ticker of your choice from STOCK_UNIVERSE: 
# a bull agent, a bear agent, and a synthesizer. Build each agent's argument from a template 
# referencing that ticker's actual beta/analyst_expected_return/std_dev numbers 
# (e.g., bull: "With an expected return of {r:.1%} against a beta of {b:.2f}, this offers attractive risk-adjusted upside."; 
# bear: references the std_dev as a risk); the synthesizer combines both into a 2–3 sentence balanced summary

import stock_universe

def get_stock_data(ticker: str):
  return stock_universe.STOCK_UNIVERSE.get(ticker)

def bull_agent(ticker):
    ticker_data = get_stock_data(ticker)
    r = ticker_data.get('analyst_expected_return')
    b = ticker_data.get('beta')
    print("Bull agent perspective:")
    print(f"With an expected return of {r:.1%} against a beta of {b:.2f}, this offers attractive risk-adjusted upside.") 
    return r, b

def bear_agent(ticker_data):
    std_dev = ticker_data.get('std_dev')
    print("Bear agent perspective:")
    print(f"However, with a standard deviation of {std_dev:.2f}, the potential for volatility and downside risk cannot be ignored.")
    return std_dev

def synthesizer(bull_arg, bear_arg):
    r, b = bull_arg
    std_dev = bear_arg
    print("Synthesizer perspective:")
    print(f"While the bull perspective highlights the potential for strong returns of {r:.1%}, the bear argument reminds us of the inherent risks with a standard deviation of {std_dev:.2f}. Investors should weigh both sides carefully before making a decision.")

#print("Debate...")
ticker = "PAYGOLD"
bull = bull_agent(ticker)
bear = bear_agent(get_stock_data(ticker))
synthesizer(bull, bear)
