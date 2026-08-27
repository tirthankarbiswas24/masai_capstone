# masai_capstone
Capstone project for Fintech and AI prpogram

# how to set up the project


# how to run the project
- For Part A — Portfolio advisory agent --> run "python advisory_agent.py"
It will execute the advisory_agent to output the portfolio returns variance and if human escalation is needed. It will also output the templated line requested in the assignment.
For {risk_tolerance} investor {investor_id}, we recommend an allocation across {tickers} with an expected portfolio return of {return:.1%} and volatility of {vol:.1%}
- For Part B — Structured disclosure extraction --> run "python extract_disclosure.py"
It will print risk_flags, sentiment and hedging_detected (True/False) for disclosures available in the disclosure_snippets.py file
- For Part C — Multi-agent debate demo --> run "python debate.py"
It will print the 3 agents templated response
- For Part D — DCF valuation calculator --> run "python dcf_calculator.py". 
It will print the sensitivity table for DCF. Along with that it will print Comparison of EV/EBITDA multple vs DCF value
The stock ticker "PAYFIN" is hardcoded in the program. We can change the value of variable "ticker" to any other ticker like "PAYRETAIL" to get details for other stocks

# summary of design decisions for each part

## How the two estimates compare DCF and EV EBITDA multiple
For PAYBOND the multiples were as given below. The DCF is significantly higher than EV/EBITDA multiple. Multiple value used is 6
EV/EBITDA  8100000.00
      DCF 36472955.04

while for PAYRETAIL the details are provided below. They are comparable. Multiple value used is 8
EV/EBITDA 10800000.00
      DCF 13181161.28

Above observation can be explained by the fact that while EBITDA, tax rate, terminal growrth rate is same for all stocks, Beta is significantly lower for PAYBOND 7.07% vs 10.67% for PAYRETAIL. Due to this DCF is significantly higher for PAYBOND as compared to PAYRETAIL (36.47 million vs 13.18 million)