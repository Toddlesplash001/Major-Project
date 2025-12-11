# test_predictor.py
from predictor import init_commodities, TopFiveWinners, SixMonthsForecast

# supply actual CSV paths (relative to your project root)
commodity_dict = {
    "arhar": "static/Arhar.csv",
    "bajra": "static/Bajra.csv",
    # add the CSVs you actually have
}

init_commodities(commodity_dict, random_seed=42)   # trains the models (may take time)
print("Top winners:", TopFiveWinners())
print("6-month summary:", SixMonthsForecast())