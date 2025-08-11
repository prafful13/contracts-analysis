# -*- coding: utf-8 -*-
"""
============================================================================
## Options Screener - FLASK BACKEND ##
============================================================================
This script is a Flask web server that acts as the backend for the
Options Screener application. It exposes an API endpoint that the React
frontend can call to get real options data.

**How it Works:**
1.  It uses Flask to create a web server.
2.  CORS is enabled to allow requests from the React frontend (which runs on a different port).
3.  It has one endpoint, `/analyze`, which accepts a POST request containing
    the user's tickers and filter criteria.
4.  It uses the exact same `yfinance` logic from our original Python script
    to fetch and analyze real-time or closing market data.
5.  It returns the results (lists of puts and calls) as a JSON response.

**To Run This Backend:**
1.  Save this file as `app.py`.
2.  Open your terminal and create a virtual environment:
    python3 -m venv venv
    source venv/bin/activate  # On Windows use venv\\Scripts\\activate
3.  Install the required libraries:
    pip install Flask flask-cors yfinance pandas pytz py_vollib
4.  Run the server:
    python app.py
5.  The server will start on http://127.0.0.1:5000. Leave this terminal window running.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import date, datetime, time, timezone
import pytz
from py_vollib.black_scholes import black_scholes
from py_vollib.black_scholes.greeks.analytical import delta, gamma, theta, vega

app = Flask(__name__)
# Enable Cross-Origin Resource Sharing to allow the frontend to communicate with this backend
CORS(app)

# Configure logging
import logging
logging.basicConfig(level=logging.DEBUG)

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

def analyze_income_options(params):
    """
    Analyzes options for income strategies (selling puts/calls).
    """
    put_tickers = params.get('putTickers', '').split(',')
    call_tickers = params.get('callTickers', '').split(',')
    filters = params.get('filters', {})
    
    all_puts = []
    all_calls = []
    today = date.today()
    risk_free_rate = get_risk_free_rate()

    # --- Process Puts ---
    for ticker_symbol in put_tickers:
        if not ticker_symbol: continue
        try:
            ticker = yf.Ticker(ticker_symbol)
            current_price, price_type = get_live_or_close_price(ticker)
            if pd.isna(current_price): continue

            for exp_str in ticker.options:
                exp_date = pd.to_datetime(exp_str).date()
                dte = (exp_date - today).days
                if not (filters.get('DTE_MIN', 0) <= dte <= filters.get('DTE_MAX', 9999)): continue

                opt_chain = ticker.option_chain(exp_str)
                puts = opt_chain.puts.to_dict('records')

                use_delta_filter = 'delta' in opt_chain.puts.columns and not opt_chain.puts['delta'].isnull().all()

                for p in puts:
                    p['otmPercent'] = (current_price - p['strike']) / current_price * 100
                    
                    common_checks = (p.get('volume', 0) >= filters.get('MIN_VOLUME', 0) and 
                                     p.get('openInterest', 0) >= filters.get('MIN_OPEN_INTEREST', 0))
                    
                    filter_passed = False
                    if use_delta_filter:
                        if (filters.get('PUT_DELTA_MIN', 0) <= abs(p.get('delta', 0)) <= filters.get('PUT_DELTA_MAX', 1)):
                            filter_passed = True
                    else: # Fallback to OTM
                        if (filters.get('PUT_OTM_PERCENT_MIN', 0) <= p['otmPercent'] <= filters.get('PUT_OTM_PERCENT_MAX', 100)):
                            filter_passed = True
                    
                    if common_checks and filter_passed:
                        premium = p.get('bid', 0)
                        p['ticker'] = ticker_symbol
                        p['premium'] = premium
                        p['DTE'] = dte
                        p['currentPrice'] = current_price
                        p['collateral'] = p['strike'] * 100
                        p['weeklyReturn'] = (premium / p['strike']) / (dte / 7) * 100 if dte > 0 and p['strike'] > 0 else 0
                        p['annualizedReturn'] = (premium / p['strike']) * (365 / dte) * 100 if dte > 0 and p['strike'] > 0 else 0
                        
                        t = dte / 365.0
                        iv = p.get('impliedVolatility', 0)
                        greeks = calculate_greeks('p', current_price, p['strike'], t, risk_free_rate, iv)
                        p.update(greeks)
                        
                        all_puts.append(p)
        except Exception as e:
            print(f"Error processing puts for {ticker_symbol}: {e}")

    # --- Process Calls ---
    for ticker_symbol in call_tickers:
        if not ticker_symbol: continue
        try:
            ticker = yf.Ticker(ticker_symbol)
            current_price, price_type = get_live_or_close_price(ticker)
            if pd.isna(current_price): continue

            for exp_str in ticker.options:
                exp_date = pd.to_datetime(exp_str).date()
                dte = (exp_date - today).days
                if not (filters.get('DTE_MIN', 0) <= dte <= filters.get('DTE_MAX', 9999)): continue

                opt_chain = ticker.option_chain(exp_str)
                calls = opt_chain.calls.to_dict('records')

                use_delta_filter = 'delta' in opt_chain.calls.columns and not opt_chain.calls['delta'].isnull().all()

                for c in calls:
                    c['otmPercent'] = (c['strike'] - current_price) / current_price * 100
                    
                    common_checks = (c.get('volume', 0) >= filters.get('MIN_VOLUME', 0) and 
                                     c.get('openInterest', 0) >= filters.get('MIN_OPEN_INTEREST', 0))
                    
                    filter_passed = False
                    if use_delta_filter:
                        if (filters.get('CALL_DELTA_MIN', 0) <= c.get('delta', 0) <= filters.get('CALL_DELTA_MAX', 1)):
                            filter_passed = True
                    else: # Fallback to OTM
                        if (filters.get('CALL_OTM_PERCENT_MIN', 0) <= c['otmPercent'] <= filters.get('CALL_OTM_PERCENT_MAX', 100)):
                            filter_passed = True
                    
                    if common_checks and filter_passed:
                        premium = c.get('bid', 0)
                        c['ticker'] = ticker_symbol
                        c['premium'] = premium
                        c['DTE'] = dte
                        c['currentPrice'] = current_price
                        c['collateral'] = current_price * 100
                        c['weeklyReturn'] = (premium / current_price) / (dte / 7) * 100 if dte > 0 and current_price > 0 else 0
                        c['annualizedReturn'] = (premium / current_price) * (365 / dte) * 100 if dte > 0 and current_price > 0 else 0
                        
                        t = dte / 365.0
                        iv = c.get('impliedVolatility', 0)
                        greeks = calculate_greeks('c', current_price, c['strike'], t, risk_free_rate, iv)
                        c.update(greeks)
                        
                        all_calls.append(c)
        except Exception as e:
            print(f"Error processing calls for {ticker_symbol}: {e}")

    return {
        'puts': all_puts,
        'calls': all_calls
    }

def analyze_buy_options(params):
    """
    Analyzes options for buying strategies.
    """
    tickers = list(set(params.get('putTickers', '').split(',') + params.get('callTickers', '').split(',')))
    filters = params.get('filters', {})

    bullish_calls = []
    bearish_puts = []
    today = date.today()
    risk_free_rate = get_risk_free_rate()

    for ticker_symbol in tickers:
        if not ticker_symbol: continue
        try:
            ticker = yf.Ticker(ticker_symbol)
            current_price, price_type = get_live_or_close_price(ticker)
            if pd.isna(current_price): continue

            for exp_str in ticker.options:
                exp_date = pd.to_datetime(exp_str).date()
                dte = (exp_date - today).days
                if not (filters.get('DTE_MIN', 0) <= dte <= filters.get('DTE_MAX', 9999)): continue

                opt_chain = ticker.option_chain(exp_str)

                # --- Process Bullish Calls ---
                calls = opt_chain.calls.to_dict('records')
                for c in calls:
                    volume = c.get('volume', 0)
                    open_interest = c.get('openInterest', 0)
                    delta_val = c.get('delta')

                    t = dte / 365.0
                    iv = c.get('impliedVolatility', 0)

                    # If yfinance fails to provide delta, calculate it manually
                    if pd.isna(delta_val) or delta_val == 0:
                        greeks = calculate_greeks('c', current_price, c['strike'], t, risk_free_rate, iv)
                        delta_val = greeks.get('delta')
                        c.update(greeks)

                    delta_val = delta_val or 0

                    if volume < filters.get('MIN_VOLUME', 0): continue
                    if open_interest < filters.get('MIN_OPEN_INTEREST', 0): continue
                    if not (filters.get('BUY_CALL_DELTA_MIN', 0.4) <= delta_val <= filters.get('BUY_CALL_DELTA_MAX', 1.0)): continue

                    c['ticker'] = ticker_symbol
                    c['DTE'] = dte
                    c['currentPrice'] = current_price
                    c['premium'] = c.get('ask', 0)

                    c['buyScore'] = (delta_val * 100) + (volume / 100) + (open_interest / 1000)
                    bullish_calls.append(c)

                # --- Process Bearish Puts ---
                puts = opt_chain.puts.to_dict('records')
                for p in puts:
                    volume = p.get('volume', 0)
                    open_interest = p.get('openInterest', 0)
                    delta_val = p.get('delta')

                    t = dte / 365.0
                    iv = p.get('impliedVolatility', 0)

                    # If yfinance fails to provide delta, calculate it manually
                    if pd.isna(delta_val) or delta_val == 0:
                        greeks = calculate_greeks('p', current_price, p['strike'], t, risk_free_rate, iv)
                        delta_val = greeks.get('delta')
                        p.update(greeks)

                    delta_val = delta_val or 0

                    if volume < filters.get('MIN_VOLUME', 0): continue
                    if open_interest < filters.get('MIN_OPEN_INTEREST', 0): continue
                    if not (filters.get('BUY_PUT_DELTA_MIN', -1.0) <= delta_val <= filters.get('BUY_PUT_DELTA_MAX', -0.4)): continue

                    p['ticker'] = ticker_symbol
                    p['DTE'] = dte
                    p['currentPrice'] = current_price
                    p['premium'] = p.get('ask', 0)

                    p['buyScore'] = (abs(delta_val) * 100) + (volume / 100) + (open_interest / 1000)
                    bearish_puts.append(p)
        except Exception as e:
            app.logger.error(f"Error processing buy analysis for {ticker_symbol}: {e}")

    return {
        'bullish_calls': bullish_calls,
        'bearish_puts': bearish_puts
    }

@app.route('/analyze', methods=['POST'])
def analyze_options():
    """
    API endpoint to analyze options based on frontend parameters.
    Routes to different analysis functions based on 'screenerType'.
    """
    params = request.json
    screener_type = params.get('screenerType', 'income')
    app.logger.info(f"Received request for screenerType: {screener_type}")

    if screener_type == 'buy':
        results = analyze_buy_options(params)
    else:
        results = analyze_income_options(params)

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
