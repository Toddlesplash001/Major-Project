# services/predictor_service.py
import os
import threading
from typing import Dict, List, Any
from flask import current_app
import predictor  # your predictor.py

_lock = threading.Lock()
_initialized = False

# default mapping (update paths to match your project)
DEFAULT_COMMODITY_DICT = {
    "arhar": "static/Arhar.csv",
    "bajra": "static/Bajra.csv",
    "barley": "static/Barley.csv",
    "copra": "static/Copra.csv",
    "cotton": "static/Cotton.csv",
    "sesamum": "static/Sesamum.csv",
    "gram": "static/Gram.csv",
    "groundnut": "static/Groundnut.csv",
    "jowar": "static/Jowar.csv",
    "maize": "static/Maize.csv",
    "masoor": "static/Masoor.csv",
    "moong": "static/Moong.csv",
    "niger": "static/Niger.csv",
    "paddy": "static/Paddy.csv",
    "ragi": "static/Ragi.csv",
    "rape": "static/Rape.csv",
    "jute": "static/Jute.csv",
    "safflower": "static/Safflower.csv",
    "soyabean": "static/Soyabean.csv",
    "sugarcane": "static/Sugarcane.csv",
    "sunflower": "static/Sunflower.csv",
    "urad": "static/Urad.csv",
    "wheat": "static/Wheat.csv"
}


def _ensure_initialized(commodity_dict: Dict[str, str] = None, random_seed: int | None = None):
    """
    Lazy-initialize predictor.commodity_list using provided commodity_dict.
    This avoids heavy work at import time.
    """
    global _initialized
    if _initialized:
        return

    with _lock:
        if _initialized:
            return
        # choose provided dict or default
        if commodity_dict is None:
            commodity_dict = DEFAULT_COMMODITY_DICT

        # If your CSVs are relative to app root, make them absolute using current_app root_path if available
        try:
            app_root = current_app.root_path
        except Exception:
            app_root = None

        safe_map = {}
        for k, v in commodity_dict.items():
            if app_root and not os.path.isabs(v):
                safe_map[k] = os.path.join(app_root, v)
            else:
                safe_map[k] = v

        # init predictor module (this trains DecisionTreeRegressor per commodity)
        predictor.init_commodities(safe_map, random_seed=random_seed)
        _initialized = True


# --- Service functions that mirror predictor's API ---

def top_five_winners(commodity_dict: Dict[str, str] = None) -> List[Any]:
    _ensure_initialized(commodity_dict)
    return predictor.TopFiveWinners()


def top_five_losers(commodity_dict: Dict[str, str] = None) -> List[Any]:
    _ensure_initialized(commodity_dict)
    return predictor.TopFiveLosers()


def six_months_forecast(commodity_dict: Dict[str, str] = None) -> List[Any]:
    _ensure_initialized(commodity_dict)
    return predictor.SixMonthsForecast()


def six_months_for_commodity(name: str, commodity_dict: Dict[str, str] = None) -> List[Any]:
    _ensure_initialized(commodity_dict)
    # predictor expects "static/Name" style name when passed to SixMonthsForecastHelper
    # the commodity.getCropName() returns something like "static/Arhar" so provide that format
    # But predictor.SixMonthsForecastHelper expects a `name` like returned by getCropName() (static/Arhar)
    # We'll attempt to find the matching commodity and use its getCropName()
    for c in predictor.commodity_list:
        # comparing lowercased partial name
        if name.lower() in str(c).lower() or name.lower() in c.getCropName().lower():
            return predictor.SixMonthsForecastHelper(c.getCropName())
    # fallback: call helper with a constructed string (may fail)
    return predictor.SixMonthsForecastHelper(f"static/{name.capitalize()}")


def twelve_months_forecast(name: str, commodity_dict: Dict[str, str] = None):
    _ensure_initialized(commodity_dict)
    return predictor.TwelveMonthsForecast(name)


def current_month_price(name: str, commodity_dict: Dict[str, str] = None):
    _ensure_initialized(commodity_dict)
    return predictor.CurrentMonth(name)


def twelve_months_previous(name: str, commodity_dict: Dict[str, str] = None):
    _ensure_initialized(commodity_dict)
    return predictor.TwelveMonthPrevious(name)
