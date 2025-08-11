import yfinance as yf
import pandas as pd
from datetime import datetime, time
import pytz
from py_vollib.black_scholes.greeks.analytical import delta, gamma, theta, vega
import math

def get_risk_free_rate():
    """
    Fetches the risk-free interest rate from the 13-week Treasury bill (^IRX).
    """
    try:
        irx = yf.Ticker("^IRX")
        # The price is given as a percentage, so divide by 100
        risk_free_rate = irx.history(period='1d')['Close'].iloc[-1] / 100
        if pd.isna(risk_free_rate):
            return 0.05 # Fallback to 5%
        return risk_free_rate
    except Exception:
        return 0.05 # Fallback to 5% if fetch fails

def calculate_greeks(flag, S, K, t, r, iv):
    """
    Calculates the greeks for an option.
    flag: 'c' for call, 'p' for put
    S: Underlying price
    K: Strike price
    t: Time to expiration in years
    r: Risk-free rate
    iv: Implied volatility
    """
    try:
        greeks = {
            "delta": delta(flag, S, K, t, r, iv),
            "gamma": gamma(flag, S, K, t, r, iv),
            "theta": theta(flag, S, K, t, r, iv),
            "vega": vega(flag, S, K, t, r, iv)
        }
        # Clean NaN values from greeks
        for k, v in greeks.items():
            if isinstance(v, float) and math.isnan(v):
                greeks[k] = None
        return greeks
    except Exception:
        return {
            "delta": None,
            "gamma": None,
            "theta": None,
            "vega": None
        }

def get_live_or_close_price(ticker):
    """
    Checks if the market is open. If so, fetches the live price.
    Otherwise, returns the last closing price.
    """
    market_tz = pytz.timezone('America/New_York')
    market_open = time(9, 30)
    market_close = time(16, 0)

    # FIX: Use timezone-aware datetime objects to avoid DeprecationWarning
    now_et = datetime.now(market_tz)

    is_market_hours = (market_open <= now_et.time() <= market_close) and (0 <= now_et.weekday() <= 4)
    price_type = "UNKNOWN"

    if is_market_hours:
        try:
            live_price = ticker.history(period='1d', interval='1m')['Close'].iloc[-1]
            if not pd.isna(live_price):
                price_type = "LIVE"
                return live_price, price_type
        except Exception:
            pass

    close_price = ticker.history(period='1d')['Close'].iloc[-1]
    price_type = "CLOSE"
    return close_price, price_type
