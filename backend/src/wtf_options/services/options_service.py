import math

import yfinance as yf
import pandas as pd
from datetime import date
import logging
from ..utils.market_data import get_risk_free_rate, calculate_greeks, get_live_or_close_price

logger = logging.getLogger(__name__)

def analyze_income_options(params):
    """
    Analyzes options for income strategies (selling puts/calls).
    """
    put_tickers = params.get('putTickers', '').split(',')
    call_tickers = params.get('callTickers', '').split(',')
    filters = params.get('filters', {})
    logger.debug(f"Starting income analysis with filters: {filters}")

    all_puts = []
    all_calls = []
    today = date.today()
    risk_free_rate = get_risk_free_rate()

    # --- Process Puts ---
    for ticker_symbol in put_tickers:
        if not ticker_symbol: continue
        logger.info(f"Processing puts for {ticker_symbol}")
        try:
            ticker = yf.Ticker(ticker_symbol)
            current_price, price_type = get_live_or_close_price(ticker)
            logger.info(f"Current price for {ticker_symbol}: {current_price}, price type: {price_type}")
            if pd.isna(current_price):
                logger.warning(f"Could not get current price for {ticker_symbol}. Skipping.")
                continue

            for exp_str in ticker.options:
                exp_date = pd.to_datetime(exp_str).date()
                dte = (exp_date - today).days

                if not (filters.get('DTE_MIN', 0) <= dte <= filters.get('DTE_MAX', 9999)):
                    logger.debug(f"Skipping expiration {exp_str} for {ticker_symbol} due to DTE: {dte}")
                    continue

                logger.info(f"Fetching option chain for {ticker_symbol} on {exp_str}")
                opt_chain = ticker.option_chain(exp_str)
                puts = opt_chain.puts.to_dict('records')
                logger.info(f"Found {len(puts)} puts for {ticker_symbol} on {exp_str}")

                use_delta_filter = 'delta' in opt_chain.puts.columns and not opt_chain.puts['delta'].isnull().all()

                for p in puts:
                    logger.debug(f"Analyzing put {p} for {ticker_symbol} on {exp_str}")
                    contract_name = f"{ticker_symbol} {exp_str} {p['strike']}P"
                    p['otmPercent'] = (current_price - p['strike']) / current_price * 100 if current_price > 0 else 0

                    # Common checks
                    if p.get('volume', 0) < filters.get('MIN_VOLUME', 0):
                        logger.debug(f"Filtering out {contract_name}: Volume {p.get('volume', 0)} < {filters.get('MIN_VOLUME', 0)}")
                        continue
                    if p.get('openInterest', 0) < filters.get('MIN_OPEN_INTEREST', 0):
                        logger.debug(f"Filtering out {contract_name}: Open Interest {p.get('openInterest', 0)} < {filters.get('MIN_OPEN_INTEREST', 0)}")
                        continue

                    # Strategy-specific filters
                    filter_passed = False
                    if use_delta_filter:
                        delta_val = abs(p.get('delta', 0))
                        if filters.get('PUT_DELTA_MIN', 0) <= delta_val <= filters.get('PUT_DELTA_MAX', 1):
                            filter_passed = True
                        else:
                            logger.debug(f"Filtering out {contract_name}: Delta {delta_val} not in range [{filters.get('PUT_DELTA_MIN', 0)}, {filters.get('PUT_DELTA_MAX', 1)}]")
                    else: # Fallback to OTM
                        if filters.get('PUT_OTM_PERCENT_MIN', 0) <= p['otmPercent'] <= filters.get('PUT_OTM_PERCENT_MAX', 100):
                            filter_passed = True
                        else:
                            logger.debug(f"Filtering out {contract_name}: OTM % {p['otmPercent']} not in range [{filters.get('PUT_OTM_PERCENT_MIN', 0)}, {filters.get('PUT_OTM_PERCENT_MAX', 100)}]")

                    if not filter_passed:
                        continue

                    logger.info(f"Contract {contract_name} passed all filters. Adding to results.")
                    premium = p.get('bid', 0)
                    if premium == 0:
                        logger.info("bid is 0, trying lastPrice")
                        premium = p.get('lastPrice', 0)
                    p['ticker'] = ticker_symbol
                    p['expirationDate'] = exp_str
                    p['premium'] = premium
                    p['DTE'] = dte
                    p['currentPrice'] = current_price
                    p['collateral'] = p['strike'] * 100
                    p['weeklyReturn'] = (premium / p['strike']) / (dte / 7) * 100 if dte > 0 and p['strike'] > 0 else 0
                    p['annualizedReturn'] = (premium / p['strike']) * (365 / dte) * 100 if dte > 0 and p['strike'] > 0 else 0
                    if math.isnan(p['volume']):
                        p['volume'] = 0
                    if math.isnan(p['openInterest']):
                        p['openInterest'] = 0

                    # Calculate greeks
                    t = dte / 365.0
                    iv = p.get('impliedVolatility', 0)
                    greeks = calculate_greeks('p', current_price, p['strike'], t, risk_free_rate, iv)
                    p.update(greeks)

                    all_puts.append(p)
        except Exception as e:
            logger.error(f"Error processing puts for {ticker_symbol}: {e}")

    # --- Process Calls ---
    for ticker_symbol in call_tickers:
        if not ticker_symbol: continue
        logger.info(f"Processing calls for {ticker_symbol}")
        try:
            ticker = yf.Ticker(ticker_symbol)
            current_price, price_type = get_live_or_close_price(ticker)
            if pd.isna(current_price):
                logger.warning(f"Could not get current price for {ticker_symbol}. Skipping.")
                continue

            for exp_str in ticker.options:
                exp_date = pd.to_datetime(exp_str).date()
                dte = (exp_date - today).days
                if not (filters.get('DTE_MIN', 0) <= dte <= filters.get('DTE_MAX', 9999)):
                    logger.debug(f"Skipping expiration {exp_str} for {ticker_symbol} due to DTE: {dte}")
                    continue

                logger.info(f"Fetching option chain for {ticker_symbol} on {exp_str}")
                opt_chain = ticker.option_chain(exp_str)
                calls = opt_chain.calls.to_dict('records')
                logger.info(f"Found {len(calls)} calls for {ticker_symbol} on {exp_str}")

                use_delta_filter = 'delta' in opt_chain.calls.columns and not opt_chain.calls['delta'].isnull().all()

                for c in calls:
                    contract_name = f"{ticker_symbol} {exp_str} {c['strike']}C"
                    c['otmPercent'] = (c['strike'] - current_price) / current_price * 100 if current_price > 0 else 0

                    if c.get('volume', 0) < filters.get('MIN_VOLUME', 0):
                        logger.debug(f"Filtering out {contract_name}: Volume {c.get('volume', 0)} < {filters.get('MIN_VOLUME', 0)}")
                        continue
                    if c.get('openInterest', 0) < filters.get('MIN_OPEN_INTEREST', 0):
                        logger.debug(f"Filtering out {contract_name}: Open Interest {c.get('openInterest', 0)} < {filters.get('MIN_OPEN_INTEREST', 0)}")
                        continue

                    filter_passed = False
                    if use_delta_filter:
                        delta_val = c.get('delta', 0)
                        if filters.get('CALL_DELTA_MIN', 0) <= delta_val <= filters.get('CALL_DELTA_MAX', 1):
                            filter_passed = True
                        else:
                            logger.debug(f"Filtering out {contract_name}: Delta {delta_val} not in range [{filters.get('CALL_DELTA_MIN', 0)}, {filters.get('CALL_DELTA_MAX', 1)}]")
                    else: # Fallback to OTM
                        if filters.get('CALL_OTM_PERCENT_MIN', 0) <= c['otmPercent'] <= filters.get('CALL_OTM_PERCENT_MAX', 100):
                            filter_passed = True
                        else:
                            logger.debug(f"Filtering out {contract_name}: OTM % {c['otmPercent']} not in range [{filters.get('CALL_OTM_PERCENT_MIN', 0)}, {filters.get('CALL_OTM_PERCENT_MAX', 100)}]")

                    if not filter_passed:
                        continue

                    logger.info(f"Contract {contract_name} passed all filters. Adding to results.")
                    premium = c.get('bid', 0)
                    if premium == 0:
                        premium = c.get('lastPrice', 0)
                    c['ticker'] = ticker_symbol
                    c['expirationDate'] = exp_str
                    c['premium'] = premium
                    c['DTE'] = dte
                    c['currentPrice'] = current_price
                    c['collateral'] = current_price * 100
                    c['weeklyReturn'] = (premium / current_price) / (dte / 7) * 100 if dte > 0 and current_price > 0 else 0
                    c['annualizedReturn'] = (premium / current_price) * (365 / dte) * 100 if dte > 0 and current_price > 0 else 0
                    if math.isnan(c['volume']):
                        c['volume'] = 0
                    if math.isnan(c['openInterest']):
                        c['openInterest'] = 0

                    # Calculate greeks
                    t = dte / 365.0
                    iv = c.get('impliedVolatility', 0)
                    greeks = calculate_greeks('c', current_price, c['strike'], t, risk_free_rate, iv)
                    c.update(greeks)

                    all_calls.append(c)
        except Exception as e:
            logger.error(f"Error processing calls for {ticker_symbol}: {e}")

    logger.info(f"Income analysis complete. Found {len(all_puts)} puts and {len(all_calls)} calls.")
    logger.debug(f"all_puts: {all_puts} and all_calls: {all_calls}")
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
    logger.debug(f"Starting buy analysis with filters: {filters}")


    bullish_calls = []
    bearish_puts = []
    today = date.today()
    risk_free_rate = get_risk_free_rate()

    for ticker_symbol in tickers:
        if not ticker_symbol: continue
        logger.info(f"Processing buy analysis for {ticker_symbol}")
        try:
            ticker = yf.Ticker(ticker_symbol)
            current_price, price_type = get_live_or_close_price(ticker)
            if pd.isna(current_price):
                logger.warning(f"Could not get current price for {ticker_symbol}. Skipping.")
                continue

            for exp_str in ticker.options:
                exp_date = pd.to_datetime(exp_str).date()
                dte = (exp_date - today).days
                if not (filters.get('DTE_MIN', 0) <= dte <= filters.get('DTE_MAX', 9999)):
                    logger.debug(f"Skipping expiration {exp_str} for {ticker_symbol} due to DTE: {dte}")
                    continue

                logger.info(f"Fetching option chain for {ticker_symbol} on {exp_str}")
                opt_chain = ticker.option_chain(exp_str)

                # --- Process Bullish Calls ---
                calls = opt_chain.calls.to_dict('records')
                logger.info(f"Found {len(calls)} calls for {ticker_symbol} on {exp_str}")
                for c in calls:
                    contract_name = f"{ticker_symbol} {exp_str} {c['strike']}C"
                    volume = c.get('volume', 0)
                    open_interest = c.get('openInterest', 0)
                    delta_val = c.get('delta')

                    t = dte / 365.0
                    iv = c.get('impliedVolatility', 0)

                    if pd.isna(delta_val) or delta_val == 0:
                        greeks = calculate_greeks('c', current_price, c['strike'], t, risk_free_rate, iv)
                        delta_val = greeks.get('delta')
                        c.update(greeks)
                    delta_val = delta_val or 0

                    if volume < filters.get('MIN_VOLUME', 0):
                        logger.debug(f"Filtering out {contract_name}: Volume {volume} < {filters.get('MIN_VOLUME', 0)}")
                        continue
                    if open_interest < filters.get('MIN_OPEN_INTEREST', 0):
                        logger.debug(f"Filtering out {contract_name}: Open Interest {open_interest} < {filters.get('MIN_OPEN_INTEREST', 0)}")
                        continue
                    if not (filters.get('BUY_CALL_DELTA_MIN', 0.4) <= delta_val <= filters.get('BUY_CALL_DELTA_MAX', 1.0)):
                        logger.debug(f"Filtering out {contract_name}: Delta {delta_val} not in range [{filters.get('BUY_CALL_DELTA_MIN', 0.4)}, {filters.get('BUY_CALL_DELTA_MAX', 1.0)}]")
                        continue

                    logger.info(f"Contract {contract_name} passed all filters. Adding to bullish calls.")
                    c['ticker'] = ticker_symbol
                    c['expirationDate'] = exp_str
                    c['DTE'] = dte
                    c['currentPrice'] = current_price
                    c['premium'] = c.get('ask', 0)
                    c['buyScore'] = (delta_val * 100) + (volume / 100) + (open_interest / 1000)
                    bullish_calls.append(c)

                # --- Process Bearish Puts ---
                puts = opt_chain.puts.to_dict('records')
                logger.info(f"Found {len(puts)} puts for {ticker_symbol} on {exp_str}")
                for p in puts:
                    contract_name = f"{ticker_symbol} {exp_str} {p['strike']}P"
                    volume = p.get('volume', 0)
                    open_interest = p.get('openInterest', 0)
                    delta_val = p.get('delta')

                    t = dte / 365.0
                    iv = p.get('impliedVolatility', 0)

                    if pd.isna(delta_val) or delta_val == 0:
                        greeks = calculate_greeks('p', current_price, p['strike'], t, risk_free_rate, iv)
                        delta_val = greeks.get('delta')
                        p.update(greeks)
                    delta_val = delta_val or 0

                    if volume < filters.get('MIN_VOLUME', 0):
                        logger.debug(f"Filtering out {contract_name}: Volume {volume} < {filters.get('MIN_VOLUME', 0)}")
                        continue
                    if open_interest < filters.get('MIN_OPEN_INTEREST', 0):
                        logger.debug(f"Filtering out {contract_name}: Open Interest {open_interest} < {filters.get('MIN_OPEN_INTEREST', 0)}")
                        continue
                    if not (filters.get('BUY_PUT_DELTA_MIN', -1.0) <= delta_val <= filters.get('BUY_PUT_DELTA_MAX', -0.4)):
                        logger.debug(f"Filtering out {contract_name}: Delta {delta_val} not in range [{filters.get('BUY_PUT_DELTA_MIN', -1.0)}, {filters.get('BUY_PUT_DELTA_MAX', -0.4)}]")
                        continue

                    logger.info(f"Contract {contract_name} passed all filters. Adding to bearish puts.")
                    p['ticker'] = ticker_symbol
                    p['expirationDate'] = exp_str
                    p['DTE'] = dte
                    p['currentPrice'] = current_price
                    p['premium'] = p.get('ask', 0)
                    p['buyScore'] = (abs(delta_val) * 100) + (volume / 100) + (open_interest / 1000)
                    bearish_puts.append(p)
        except Exception as e:
            logger.error(f"Error processing buy analysis for {ticker_symbol}: {e}")

    logger.info(f"Buy analysis complete. Found {len(bullish_calls)} bullish calls and {len(bearish_puts)} bearish puts.")
    return {
        'bullish_calls': bullish_calls,
        'bearish_puts': bearish_puts
    }
