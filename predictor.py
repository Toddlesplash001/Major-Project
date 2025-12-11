# predictor.py
# Prediction module extracted from the original combined app.
# Provides Commodity class and functions:
# TopFiveWinners, TopFiveLosers, SixMonthsForecast,
# SixMonthsForecastHelper, CurrentMonth, TwelveMonthsForecast,
# TwelveMonthPrevious, init_commodities

from datetime import datetime
import numpy as np
import pandas as pd
import random

# annual rainfall (kept from original)
ANNUAL_RAINFALL = [29, 21, 37.5, 30.7, 52.6, 150, 299, 251.7, 179.2, 70.5, 39.8, 10.9]

# base price mapping (kept from original)
BASE = {
    "Paddy": 1245.5,
    "Arhar": 3200,
    "Bajra": 1175,
    "Barley": 980,
    "Copra": 5100,
    "Cotton": 3600,
    "Sesamum": 4200,
    "Gram": 2800,
    "Groundnut": 3700,
    "Jowar": 1520,
    "Maize": 1175,
    "Masoor": 2800,
    "Moong": 3500,
    "Niger": 3500,
    "Ragi": 1500,
    "Rape": 2500,
    "Jute": 1675,
    "Safflower": 2500,
    "Soyabean": 2200,
    "Sugarcane": 2250,
    "Sunflower": 3700,
    "Urad": 4300,
    "Wheat": 1350
}

# Global commodity list (filled by init_commodities)
commodity_list = []


class Commodity:
    """
    Commodity predictor - wraps a DecisionTreeRegressor trained on the provided CSV.
    csv_name: path to CSV file (expects same format as original code)
    """

    def __init__(self, csv_name, random_seed=None):
        self.name = csv_name  # e.g. "static/Arhar.csv"
        dataset = pd.read_csv(csv_name)
        # original code used all columns except last as X and column 3 as Y
        self.X = dataset.iloc[:, :-1].values
        self.Y = dataset.iloc[:, 3].values

        # Fit Decision Tree (similar to original)
        from sklearn.tree import DecisionTreeRegressor
        if random_seed is not None:
            random.seed(random_seed)
        depth = random.randrange(7, 18)
        self.regressor = DecisionTreeRegressor(max_depth=depth)
        self.regressor.fit(self.X, self.Y)

    def getPredictedValue(self, value):
        """
        value: list/tuple with 3 items [month(float), year(int), rainfall(float)]
        Behavior:
          - If year >= 2019: predict using regressor
          - Else: return historical exact Y for the matching (month, year) pair (same logic as original)
        """
        if value[1] >= 2019:
            fsa = np.array(value).reshape(1, 3)
            return float(self.regressor.predict(fsa)[0])
        else:
            # find matching (month, year) pair in stored X[:,0:2]
            c = self.X[:, 0:2]
            x_pairs = [list(i) for i in c]
            target = [value[0], value[1]]
            ind = 0
            for idx, pair in enumerate(x_pairs):
                if pair == target:
                    ind = idx
                    break
            # return the corresponding Y value (fixed bug: use ind)
            return float(self.Y[ind])

    def getCropName(self):
        # preserve original behavior: return csv filename without extension
        a = self.name.split('.')
        return a[0]  # e.g. "static/Arhar"


# ---------- Helper / public functions (same names as original app) ----------

def init_commodities(commodity_dict, random_seed=None):
    """
    Initialize commodity_list from a dict mapping shortname -> csv_path.
    Example commodity_dict:
      {"arhar": "static/Arhar.csv", "bajra": "static/Bajra.csv", ...}
    This function clears & repopulates the global commodity_list.
    """
    global commodity_list
    commodity_list = []
    # create Commodity objects in the same order as original script
    for key in commodity_dict:
        c = Commodity(commodity_dict[key], random_seed=random_seed)
        commodity_list.append(c)


def TopFiveWinners():
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_rainfall = ANNUAL_RAINFALL[current_month - 1]
    prev_month = current_month - 1
    prev_rainfall = ANNUAL_RAINFALL[prev_month - 1]
    current_month_prediction = []
    prev_month_prediction = []
    change = []

    for i in commodity_list:
        current_predict = i.getPredictedValue([float(current_month), current_year, current_rainfall])
        current_month_prediction.append(current_predict)
        prev_predict = i.getPredictedValue([float(prev_month), current_year, prev_rainfall])
        prev_month_prediction.append(prev_predict)
        change.append((((current_predict - prev_predict) * 100 / prev_predict), commodity_list.index(i)))
    sorted_change = sorted(change, reverse=True)
    to_send = []
    for j in range(0, min(5, len(sorted_change))):
        perc, idx = sorted_change[j]
        name = commodity_list[idx].getCropName().split('/')[1]
        to_send.append([name, round((current_month_prediction[idx] * BASE[name]) / 100, 2), round(perc, 2)])
    return to_send


def TopFiveLosers():
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_rainfall = ANNUAL_RAINFALL[current_month - 1]
    prev_month = current_month - 1
    prev_rainfall = ANNUAL_RAINFALL[prev_month - 1]
    current_month_prediction = []
    prev_month_prediction = []
    change = []

    for i in commodity_list:
        current_predict = i.getPredictedValue([float(current_month), current_year, current_rainfall])
        current_month_prediction.append(current_predict)
        prev_predict = i.getPredictedValue([float(prev_month), current_year, prev_rainfall])
        prev_month_prediction.append(prev_predict)
        change.append((((current_predict - prev_predict) * 100 / prev_predict), commodity_list.index(i)))
    sorted_change = sorted(change)  # ascending
    to_send = []
    for j in range(0, min(5, len(sorted_change))):
        perc, idx = sorted_change[j]
        name = commodity_list[idx].getCropName().split('/')[1]
        to_send.append([name, round((current_month_prediction[idx] * BASE[name]) / 100, 2), round(perc, 2)])
    return to_send


def SixMonthsForecast():
    month1 = []
    month2 = []
    month3 = []
    month4 = []
    month5 = []
    month6 = []
    for i in commodity_list:
        crop = SixMonthsForecastHelper(i.getCropName())
        k = 0
        for j in crop:
            time = j[0]
            price = j[1]
            change = j[2]
            if k == 0:
                month1.append((price, change, i.getCropName().split("/")[1], time))
            elif k == 1:
                month2.append((price, change, i.getCropName().split("/")[1], time))
            elif k == 2:
                month3.append((price, change, i.getCropName().split("/")[1], time))
            elif k == 3:
                month4.append((price, change, i.getCropName().split("/")[1], time))
            elif k == 4:
                month5.append((price, change, i.getCropName().split("/")[1], time))
            elif k == 5:
                month6.append((price, change, i.getCropName().split("/")[1], time))
            k += 1
    month1.sort()
    month2.sort()
    month3.sort()
    month4.sort()
    month5.sort()
    month6.sort()
    crop_month_wise = []
    arrays = [month1, month2, month3, month4, month5, month6]
    for arr in arrays:
        if not arr:
            # in case of missing data, append placeholders
            crop_month_wise.append([None, None, None, None, None, None, None])
            continue
        crop_month_wise.append([
            arr[0][3],                 # month label (min)
            arr[-1][2],                # max crop name
            arr[-1][0],                # max price
            arr[-1][1],                # max change
            arr[0][2],                 # min crop name
            arr[0][0],                 # min price
            arr[0][1]                  # min change
        ])
    return crop_month_wise


def SixMonthsForecastHelper(name):
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_rainfall = ANNUAL_RAINFALL[current_month - 1]
    # name passed as "static/Arhar" in original - keep same flow
    name = name.split("/")[1]
    name = name.lower()
    # find commodity object by matching string conversion (similar to original)
    commodity = commodity_list[0]
    for i in commodity_list:
        if name == str(i):
            commodity = i
            break
    month_with_year = []
    for i in range(1, 7):
        if current_month + i <= 12:
            month_with_year.append((current_month + i, current_year, ANNUAL_RAINFALL[current_month + i - 1]))
        else:
            month_with_year.append((current_month + i - 12, current_year + 1, ANNUAL_RAINFALL[current_month + i - 13]))
    wpis = []
    current_wpi = commodity.getPredictedValue([float(current_month), current_year, current_rainfall])
    change = []
    for m, y, r in month_with_year:
        current_predict = commodity.getPredictedValue([float(m), y, r])
        wpis.append(current_predict)
        change.append(((current_predict - current_wpi) * 100) / current_wpi)
    crop_price = []
    for i in range(0, len(wpis)):
        m, y, r = month_with_year[i]
        x = datetime(y, m, 1)
        x = x.strftime("%b %y")
        crop_price.append([x, round((wpis[i] * BASE[name.capitalize()]) / 100, 2), round(change[i], 2)])
    return crop_price


def CurrentMonth(name):
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_rainfall = ANNUAL_RAINFALL[current_month - 1]
    name = name.lower()
    commodity = commodity_list[0]
    for i in commodity_list:
        if name == str(i):
            commodity = i
            break
    current_wpi = commodity.getPredictedValue([float(current_month), current_year, current_rainfall])
    current_price = (BASE[name.capitalize()] * current_wpi) / 100
    return current_price


def TwelveMonthsForecast(name):
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_rainfall = ANNUAL_RAINFALL[current_month - 1]
    name = name.lower()
    commodity = commodity_list[0]
    for i in commodity_list:
        if name == str(i):
            commodity = i
            break
    month_with_year = []
    for i in range(1, 13):
        if current_month + i <= 12:
            month_with_year.append((current_month + i, current_year, ANNUAL_RAINFALL[current_month + i - 1]))
        else:
            month_with_year.append((current_month + i - 12, current_year + 1, ANNUAL_RAINFALL[current_month + i - 13]))
    max_index = 0
    min_index = 0
    max_value = -float('inf')
    min_value = float('inf')
    wpis = []
    current_wpi = commodity.getPredictedValue([float(current_month), current_year, current_rainfall])
    change = []
    for m, y, r in month_with_year:
        current_predict = commodity.getPredictedValue([float(m), y, r])
        if current_predict > max_value:
            max_value = current_predict
            max_index = month_with_year.index((m, y, r))
        if current_predict < min_value:
            min_value = current_predict
            min_index = month_with_year.index((m, y, r))
        wpis.append(current_predict)
        change.append(((current_predict - current_wpi) * 100) / current_wpi)
    max_month, max_year, r1 = month_with_year[max_index]
    min_month, min_year, r2 = month_with_year[min_index]
    min_value = min_value * BASE[name.capitalize()] / 100
    max_value = max_value * BASE[name.capitalize()] / 100
    crop_price = []
    for i in range(0, len(wpis)):
        m, y, r = month_with_year[i]
        x = datetime(y, m, 1)
        x = x.strftime("%b %y")
        crop_price.append([x, round((wpis[i] * BASE[name.capitalize()]) / 100, 2), round(change[i], 2)])
    x = datetime(max_year, max_month, 1)
    x = x.strftime("%b %y")
    max_crop = [x, round(max_value, 2)]
    x = datetime(min_year, min_month, 1)
    x = x.strftime("%b %y")
    min_crop = [x, round(min_value, 2)]
    return max_crop, min_crop, crop_price


def TwelveMonthPrevious(name):
    name = name.lower()
    current_month = datetime.now().month
    current_year = datetime.now().year
    # current_rainfall is not used for historical retrieval in original code
    commodity = commodity_list[0]
    wpis = []
    crop_price = []
    for i in commodity_list:
        if name == str(i):
            commodity = i
            break
    month_with_year = []
    for i in range(1, 13):
        if current_month - i >= 1:
            month_with_year.append((current_month - i, current_year, ANNUAL_RAINFALL[current_month - i - 1]))
        else:
            month_with_year.append((current_month - i + 12, current_year - 1, ANNUAL_RAINFALL[current_month - i + 11]))
    for m, y, r in month_with_year:
        current_predict = commodity.getPredictedValue([float(m), 2013, r])  # original used year 2013
        wpis.append(current_predict)
    for i in range(0, len(wpis)):
        m, y, r = month_with_year[i]
        x = datetime(y, m, 1)
        x = x.strftime("%b %y")
        crop_price.append([x, round((wpis[i] * BASE[name.capitalize()]) / 100, 2)])
    new_crop_price = []
    for i in range(len(crop_price) - 1, -1, -1):
        new_crop_price.append(crop_price[i])
    return new_crop_price
