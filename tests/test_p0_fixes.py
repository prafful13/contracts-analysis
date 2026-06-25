from __future__ import annotations

import math
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


class TestIsNanNoneFix:
    """Issue #7 — pd.isna handles None; math.isnan raises TypeError on None."""

    def _make_option_dict(self, volume, open_interest: int | None = 100) -> dict:
        return {
            "strike": 150.0,
            "lastPrice": 1.5,
            "bid": 1.4,
            "ask": 1.6,
            "volume": volume,
            "openInterest": open_interest,
            "impliedVolatility": 0.3,
            "delta": None,
        }

    def _minimal_params(self, puts_ticker: str = "AAPL") -> dict:
        return {
            "putTickers": puts_ticker,
            "callTickers": "",
            "filters": {
                "DTE_MIN": 0,
                "DTE_MAX": 9999,
                "MIN_VOLUME": 0,
                "MIN_OPEN_INTEREST": 0,
                "PUT_OTM_PERCENT_MIN": -100,
                "PUT_OTM_PERCENT_MAX": 100,
                "MIN_RETURN": 0,
            },
        }

    def _mock_ticker(self, put_record: dict, exp: str = "2026-09-19") -> MagicMock:
        import pandas as pd
        from datetime import date

        ticker = MagicMock()
        ticker.options = [exp]
        chain = MagicMock()
        chain.puts = pd.DataFrame([put_record])
        chain.calls = pd.DataFrame()
        ticker.option_chain.return_value = chain
        return ticker

    def test_none_volume_does_not_raise(self):
        """volume=None must be normalised to 0, not raise TypeError."""
        from wtf_options.services.options_service import analyze_income_options

        put_record = self._make_option_dict(volume=None, open_interest=50)
        ticker = self._mock_ticker(put_record)

        with (
            patch("wtf_options.services.options_service.yf.Ticker", return_value=ticker),
            patch("wtf_options.services.options_service.get_live_or_close_price", return_value=(150.0, "CLOSE")),
            patch("wtf_options.services.options_service.get_risk_free_rate", return_value=0.05),
            patch("wtf_options.services.options_service.calculate_greeks", return_value={"delta": -0.3, "gamma": 0.01, "theta": -0.05, "vega": 0.1}),
        ):
            result = analyze_income_options(self._minimal_params())

        puts = result["puts"]
        assert len(puts) == 1
        assert puts[0]["volume"] == 0

    def test_none_open_interest_does_not_raise(self):
        """openInterest=None must be normalised to 0, not raise TypeError."""
        from wtf_options.services.options_service import analyze_income_options

        put_record = self._make_option_dict(volume=10, open_interest=None)
        ticker = self._mock_ticker(put_record)

        with (
            patch("wtf_options.services.options_service.yf.Ticker", return_value=ticker),
            patch("wtf_options.services.options_service.get_live_or_close_price", return_value=(150.0, "CLOSE")),
            patch("wtf_options.services.options_service.get_risk_free_rate", return_value=0.05),
            patch("wtf_options.services.options_service.calculate_greeks", return_value={"delta": -0.3, "gamma": 0.01, "theta": -0.05, "vega": 0.1}),
        ):
            result = analyze_income_options(self._minimal_params())

        puts = result["puts"]
        assert len(puts) == 1
        assert puts[0]["openInterest"] == 0

    def test_float_nan_volume_is_also_normalised(self):
        """float NaN must still be normalised (regression guard)."""
        from wtf_options.services.options_service import analyze_income_options

        put_record = self._make_option_dict(volume=float("nan"), open_interest=float("nan"))
        ticker = self._mock_ticker(put_record)

        with (
            patch("wtf_options.services.options_service.yf.Ticker", return_value=ticker),
            patch("wtf_options.services.options_service.get_live_or_close_price", return_value=(150.0, "CLOSE")),
            patch("wtf_options.services.options_service.get_risk_free_rate", return_value=0.05),
            patch("wtf_options.services.options_service.calculate_greeks", return_value={"delta": -0.3, "gamma": 0.01, "theta": -0.05, "vega": 0.1}),
        ):
            result = analyze_income_options(self._minimal_params())

        puts = result["puts"]
        assert len(puts) == 1
        assert puts[0]["volume"] == 0
        assert puts[0]["openInterest"] == 0


class TestEmptyHistoryFix:
    """Issue #8 — iloc[-1] on empty history must return (nan, UNAVAILABLE)."""

    def test_empty_history_returns_nan_unavailable(self):
        from wtf_options.utils.market_data import get_live_or_close_price

        ticker = MagicMock()
        empty_series = pd.Series([], dtype=float)
        ticker.history.return_value = pd.DataFrame({"Close": empty_series})

        price, price_type = get_live_or_close_price(ticker)

        assert math.isnan(price)
        assert price_type == "UNAVAILABLE"

    def test_unavailable_ticker_excluded_from_results(self):
        """Service must skip the ticker and record it in unavailable_tickers."""
        from wtf_options.services.options_service import analyze_income_options

        with (
            patch("wtf_options.services.options_service.yf.Ticker"),
            patch("wtf_options.services.options_service.get_live_or_close_price", return_value=(float("nan"), "UNAVAILABLE")),
            patch("wtf_options.services.options_service.get_risk_free_rate", return_value=0.05),
        ):
            result = analyze_income_options({
                "putTickers": "AAPL,NVDA",
                "callTickers": "",
                "filters": {},
            })

        assert result["puts"] == []
        assert set(result["unavailable_tickers"]) == {"AAPL", "NVDA"}
