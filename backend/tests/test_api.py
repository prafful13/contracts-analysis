import pytest
import pandas as pd
from backend.app import app
from datetime import date, timedelta

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def get_mock_ticker(mocker, puts_data, calls_data):
    mock_ticker = mocker.MagicMock()
    mock_ticker.history.return_value = pd.DataFrame({'Close': [100.0]})

    mock_puts = pd.DataFrame(puts_data)
    mock_calls = pd.DataFrame(calls_data)

    # Ensure all required columns are present with default values
    for df in [mock_puts, mock_calls]:
        for col in ['strike', 'lastPrice', 'volume', 'openInterest', 'impliedVolatility', 'delta', 'bid', 'ask', 'change', 'contractSize', 'currency', 'inTheMoney', 'lastTradeDate', 'otmPercent', 'percentChange']:
            if col not in df.columns:
                df[col] = 0

    mock_option_chain = mocker.MagicMock()
    mock_option_chain.puts = mock_puts
    mock_option_chain.calls = mock_calls

    mock_ticker.option_chain.return_value = mock_option_chain

    exp_date = date.today() + timedelta(days=15)
    mock_ticker.options = [exp_date.strftime('%Y-%m-%d')]

    return mock_ticker

def test_analyze_income_options(client, mocker):
    puts_data = {
        'strike': [90], 'volume': [100], 'openInterest': [100], 'delta': [0.2], 'bid': [0.5], 'impliedVolatility': [0.5]
    }
    calls_data = {
        'strike': [110], 'volume': [100], 'openInterest': [100], 'delta': [0.3], 'bid': [0.6], 'impliedVolatility': [0.5]
    }

    mock_ticker_instance = get_mock_ticker(mocker, puts_data, calls_data)
    mocker.patch('yfinance.Ticker', return_value=mock_ticker_instance)
    mocker.patch('backend.utils.market_data.get_risk_free_rate', return_value=0.05)

    response = client.post('/analyze', json={
        'screenerType': 'income',
        'putTickers': 'AAPL',
        'callTickers': 'GOOG',
        'filters': {
            'DTE_MIN': 0,
            'DTE_MAX': 30,
            'MIN_VOLUME': 50,
            'MIN_OPEN_INTEREST': 50
        }
    })

    assert response.status_code == 200
    data = response.json
    assert 'puts' in data
    assert 'calls' in data
    assert len(data['puts']) == 1
    assert len(data['calls']) == 1
    assert data['puts'][0]['ticker'] == 'AAPL'
    assert data['calls'][0]['ticker'] == 'GOOG'

def test_analyze_buy_options(client, mocker):
    puts_data = {
        'strike': [90], 'volume': [100], 'openInterest': [100], 'delta': [-0.5], 'ask': [0.5], 'impliedVolatility': [0.5]
    }
    calls_data = {
        'strike': [110], 'volume': [100], 'openInterest': [100], 'delta': [0.5], 'ask': [0.6], 'impliedVolatility': [0.5]
    }

    # Since we are passing two different tickers, the mock needs to handle being called for each
    def get_mock_ticker_for_symbol(symbol):
        return get_mock_ticker(mocker, puts_data, calls_data)

    mocker.patch('yfinance.Ticker', side_effect=get_mock_ticker_for_symbol)
    mocker.patch('backend.utils.market_data.get_risk_free_rate', return_value=0.05)

    response = client.post('/analyze', json={
        'screenerType': 'buy',
        'putTickers': 'AAPL',
        'callTickers': 'GOOG',
        'filters': {
            'DTE_MIN': 0,
            'DTE_MAX': 30,
            'MIN_VOLUME': 50,
            'MIN_OPEN_INTEREST': 50,
            'BUY_CALL_DELTA_MIN': 0.4,
            'BUY_CALL_DELTA_MAX': 1.0,
            'BUY_PUT_DELTA_MIN': -1.0,
            'BUY_PUT_DELTA_MAX': -0.4,
        }
    })

    assert response.status_code == 200
    data = response.json
    assert 'bullish_calls' in data
    assert 'bearish_puts' in data
    assert len(data['bullish_calls']) == 2
    assert len(data['bearish_puts']) == 2

    call_tickers = sorted([d['ticker'] for d in data['bullish_calls']])
    put_tickers = sorted([d['ticker'] for d in data['bearish_puts']])

    assert call_tickers == ['AAPL', 'GOOG']
    assert put_tickers == ['AAPL', 'GOOG']
