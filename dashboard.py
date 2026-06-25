"""Options Screener — Streamlit dashboard."""
from __future__ import annotations

import logging
import os
import sys

import pandas as pd
import streamlit as st
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "src"))
from wtf_options.services.options_service import analyze_buy_options, analyze_income_options  # noqa: E402

logging.basicConfig(level=logging.WARNING)

st.set_page_config(
    page_title="Options Screener",
    page_icon="Ω",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Options Screener — for educational use only. Not financial advice."},
)

# ── Config ──────────────────────────────────────────────────────────────────
_cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
with open(_cfg_path) as _f:
    _CFG = yaml.safe_load(_f)

FILTERS = _CFG["filters"]
SCREENER = _CFG["screener"]

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Target text nodes only — avoid div/span which breaks Streamlit icon pseudo-elements */
html, body, .stApp, p, h1, h2, h3, h4, h5, h6,
button, label, input, textarea,
[data-testid="stSidebarContent"],
[data-testid="stMarkdownContainer"],
[data-testid="stExpander"] summary p,
[data-testid="stTab"] button p {
    font-family: 'Space Grotesk', system-ui, -apple-system, sans-serif !important;
}

[data-testid="stDataFrame"] td {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}

[data-testid="stMetricLabel"] p {
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    opacity: 0.5;
}

[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 22px !important;
    font-weight: 600 !important;
}

.stTextArea textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    line-height: 1.6 !important;
}

.stNumberInput input {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }

.sidebar-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    opacity: 0.4;
    margin: 16px 0 4px 0;
    display: block;
}

.app-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}

.app-logo {
    width: 32px;
    height: 32px;
    background: #E6C547;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 800;
    color: #0D1117;
    flex-shrink: 0;
}

.app-title { font-size: 16px; font-weight: 700; letter-spacing: -0.02em; }
.app-sub { font-size: 11px; opacity: 0.35; margin-top: 1px; }

.stDownloadButton > button {
    font-size: 11px !important;
    padding: 4px 14px !important;
    height: auto !important;
}
</style>
""", unsafe_allow_html=True)

# ── Column definitions ───────────────────────────────────────────────────────
INCOME_COLS = [
    "ticker", "expirationDate", "DTE", "strike", "currentPrice",
    "premium", "delta", "otmPercent", "impliedVolatility",
    "weeklyReturn", "annualizedReturn",
]

BUY_COLS = [
    "buyScore", "ticker", "expirationDate", "DTE", "strike",
    "currentPrice", "premium", "delta", "impliedVolatility",
    "volume", "openInterest",
]


def _col_config(df: pd.DataFrame, sort_col: str) -> dict:
    max_val = float(df[sort_col].max()) * 1.1 if (not df.empty and sort_col in df.columns) else 1.0
    max_val = max(max_val, 0.01)
    return {
        "ticker": st.column_config.TextColumn("Ticker", width="small"),
        "expirationDate": st.column_config.TextColumn("Expiry", width="small"),
        "DTE": st.column_config.NumberColumn("DTE", format="%d"),
        "strike": st.column_config.NumberColumn("Strike", format="$%.2f"),
        "currentPrice": st.column_config.NumberColumn("Price", format="$%.2f"),
        "premium": st.column_config.NumberColumn("Premium", format="$%.3f"),
        "delta": st.column_config.NumberColumn(
            "Δ", format="%.3f",
            help="Probability of expiring ITM (0–1). Selling: lower is safer.",
        ),
        "otmPercent": st.column_config.NumberColumn(
            "OTM%", format="%.1f%%",
            help="Strike distance from stock price. Higher = more conservative.",
        ),
        "impliedVolatility": st.column_config.NumberColumn(
            "IV", format="%.1f%%",
            help="Implied volatility — market's expectation of future moves.",
        ),
        "weeklyReturn": st.column_config.NumberColumn(
            "Wkly%", format="%.2f%%",
            help="Premium / Collateral × (7 / DTE)",
        ),
        "annualizedReturn": st.column_config.ProgressColumn(
            "Annual%",
            format="%.1f%%",
            min_value=0.0,
            max_value=max_val,
            width="medium",
            help="Premium / Collateral × (365 / DTE) — primary income metric.",
        ),
        "collateral": st.column_config.NumberColumn(
            "Collateral", format="$%d",
            help="Cash required to secure 1 contract (100 shares × strike).",
        ),
        "buyScore": st.column_config.ProgressColumn(
            "Score",
            format="%.0f",
            min_value=0.0,
            max_value=max_val,
            help="Delta×100 + Volume÷100 + Open Interest÷1000",
        ),
        "volume": st.column_config.NumberColumn("Volume", format="%d"),
        "openInterest": st.column_config.NumberColumn("Open Int.", format="%d"),
    }


def render_table(data: list[dict], cols: list[str], sort_col: str, label: str) -> None:
    if not data:
        st.info(f"No {label} found. Try widening your delta range or DTE window.", icon="📭")
        return

    available = [c for c in cols if c in data[0]]
    df = (
        pd.DataFrame(data)[available]
        .sort_values(sort_col, ascending=False)
        .reset_index(drop=True)
    )

    st.dataframe(df, column_config=_col_config(df, sort_col), use_container_width=True, hide_index=True)

    col_dl, col_ct, _ = st.columns([1, 1, 5])
    with col_dl:
        st.download_button(
            "Export CSV",
            data=df.to_csv(index=False),
            file_name=f"{label.lower().replace(' ', '-')}.csv",
            mime="text/csv",
            key=f"dl_{label}",
        )
    with col_ct:
        st.caption(f"{len(df)} contracts")


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="app-header">'
        '<div class="app-logo">Ω</div>'
        '<div><div class="app-title">Options Screener</div>'
        '<div class="app-sub">Educational use only</div></div>'
        "</div>",
        unsafe_allow_html=True,
    )

    screener_type = st.radio("Mode", ["Income", "Buy"], horizontal=True, label_visibility="collapsed")

    st.markdown('<span class="sidebar-label">Tickers</span>', unsafe_allow_html=True)
    if screener_type == "Income":
        put_tickers_raw = st.text_area(
            "Puts — stocks to potentially buy",
            SCREENER["income"]["put_tickers"],
            height=90,
            help="Sell cash-secured puts on these. Comma-separated.",
        )
        call_tickers_raw = st.text_area(
            "Calls — stocks you already own",
            SCREENER["income"]["call_tickers"],
            height=68,
            help="Sell covered calls on these. Comma-separated.",
        )
    else:
        put_tickers_raw = st.text_area("Tickers to scan", SCREENER["buy"]["tickers"], height=90)
        call_tickers_raw = ""

    st.markdown('<span class="sidebar-label">DTE & Liquidity</span>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        dte_min = st.number_input("DTE Min", min_value=0, max_value=365, value=int(FILTERS["dte_min"]))
    with c2:
        dte_max = st.number_input("DTE Max", min_value=0, max_value=365, value=int(FILTERS["dte_max"]))
    c3, c4 = st.columns(2)
    with c3:
        min_volume = st.number_input("Min Volume", min_value=0, value=int(FILTERS["min_volume"]))
    with c4:
        min_oi = st.number_input("Min OI", min_value=0, value=int(FILTERS["min_open_interest"]))

    st.markdown('<span class="sidebar-label">Δ Delta — Primary Filter</span>', unsafe_allow_html=True)
    if screener_type == "Income":
        c5, c6 = st.columns(2)
        with c5:
            put_delta_min = st.number_input("Put Δ Min", 0.0, 1.0, float(FILTERS["put_delta_min"]), 0.01, "%.2f")
            call_delta_min = st.number_input("Call Δ Min", 0.0, 1.0, float(FILTERS["call_delta_min"]), 0.01, "%.2f")
        with c6:
            put_delta_max = st.number_input("Put Δ Max", 0.0, 1.0, float(FILTERS["put_delta_max"]), 0.01, "%.2f")
            call_delta_max = st.number_input("Call Δ Max", 0.0, 1.0, float(FILTERS["call_delta_max"]), 0.01, "%.2f")
        with st.expander("OTM% Fallback (after hours)"):
            st.caption("Used when delta is unavailable (market closed).")
            c7, c8 = st.columns(2)
            with c7:
                put_otm_min = st.number_input("Put OTM% Min", 0.0, 100.0, float(FILTERS["put_otm_percent_min"]), 0.5, "%.1f")
                call_otm_min = st.number_input("Call OTM% Min", 0.0, 100.0, float(FILTERS["call_otm_percent_min"]), 0.5, "%.1f")
            with c8:
                put_otm_max = st.number_input("Put OTM% Max", 0.0, 100.0, float(FILTERS["put_otm_percent_max"]), 0.5, "%.1f")
                call_otm_max = st.number_input("Call OTM% Max", 0.0, 100.0, float(FILTERS["call_otm_percent_max"]), 0.5, "%.1f")
    else:
        c5, c6 = st.columns(2)
        with c5:
            buy_call_delta_min = st.number_input("Call Δ Min", 0.0, 1.0, float(FILTERS["buy_call_delta_min"]), 0.01, "%.2f")
            buy_put_delta_max = st.number_input("Put Δ Max", -1.0, 0.0, float(FILTERS["buy_put_delta_max"]), 0.01, "%.2f")
        with c6:
            buy_call_delta_max = st.number_input("Call Δ Max", 0.0, 1.0, float(FILTERS["buy_call_delta_max"]), 0.01, "%.2f")
            buy_put_delta_min = st.number_input("Put Δ Min", -1.0, 0.0, float(FILTERS["buy_put_delta_min"]), 0.01, "%.2f")

    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("▶  Run Scan", type="primary", use_container_width=True)


# ── Params builder ────────────────────────────────────────────────────────────
def _build_params() -> dict:
    filters: dict = {
        "DTE_MIN": dte_min,
        "DTE_MAX": dte_max,
        "MIN_VOLUME": min_volume,
        "MIN_OPEN_INTEREST": min_oi,
    }
    if screener_type == "Income":
        filters.update({
            "PUT_DELTA_MIN": put_delta_min,
            "PUT_DELTA_MAX": put_delta_max,
            "CALL_DELTA_MIN": call_delta_min,
            "CALL_DELTA_MAX": call_delta_max,
            "PUT_OTM_PERCENT_MIN": put_otm_min,
            "PUT_OTM_PERCENT_MAX": put_otm_max,
            "CALL_OTM_PERCENT_MIN": call_otm_min,
            "CALL_OTM_PERCENT_MAX": call_otm_max,
        })
    else:
        filters.update({
            "BUY_CALL_DELTA_MIN": buy_call_delta_min,
            "BUY_CALL_DELTA_MAX": buy_call_delta_max,
            "BUY_PUT_DELTA_MIN": buy_put_delta_min,
            "BUY_PUT_DELTA_MAX": buy_put_delta_max,
        })
    return {
        "screenerType": screener_type.lower(),
        "putTickers": put_tickers_raw.upper().replace(" ", "").strip(","),
        "callTickers": call_tickers_raw.upper().replace(" ", "").strip(",") if call_tickers_raw else "",
        "filters": filters,
    }


# ── Run analysis ──────────────────────────────────────────────────────────────
if run_btn:
    with st.spinner("Fetching option chains from Yahoo Finance…"):
        try:
            params = _build_params()
            if screener_type == "Income":
                results = analyze_income_options(params)
            else:
                results = analyze_buy_options(params)
            st.session_state["results"] = results
            st.session_state["last_screener"] = screener_type
        except Exception as exc:
            st.error(f"Analysis failed: {exc}", icon="🛑")


# ── Results ───────────────────────────────────────────────────────────────────
if "results" in st.session_state:
    results = st.session_state["results"]
    last_screener = st.session_state["last_screener"]

    if last_screener == "Income":
        puts = results.get("puts", [])
        calls = results.get("calls", [])
        unavailable = results.get("unavailable_tickers", [])
        if unavailable:
            st.warning(f"Price data unavailable for: {', '.join(unavailable)} — market may be closed or tickers delisted. These were excluded from results.")
        all_returns = [r["annualizedReturn"] for r in puts + calls if r.get("annualizedReturn")]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", len(puts) + len(calls))
        m2.metric("Puts", len(puts))
        m3.metric("Calls", len(calls))
        m4.metric("Best Annual%", f"{max(all_returns):.1f}%" if all_returns else "—")

        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Cash-Secured Puts", "Covered Calls"])
        with t1:
            render_table(puts, INCOME_COLS, "annualizedReturn", "puts")
        with t2:
            render_table(calls, INCOME_COLS, "annualizedReturn", "covered calls")
    else:
        bull = results.get("bullish_calls", [])
        bear = results.get("bearish_puts", [])
        unavailable = results.get("unavailable_tickers", [])
        if unavailable:
            st.warning(f"Price data unavailable for: {', '.join(unavailable)} — market may be closed or tickers delisted. These were excluded from results.")
        all_scores = [r["buyScore"] for r in bull + bear if r.get("buyScore")]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", len(bull) + len(bear))
        m2.metric("Bullish Calls", len(bull))
        m3.metric("Bearish Puts", len(bear))
        m4.metric("Best Score", f"{max(all_scores):.0f}" if all_scores else "—")

        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Bullish — Calls to Buy", "Bearish — Puts to Buy"])
        with t1:
            render_table(bull, BUY_COLS, "buyScore", "bullish calls")
        with t2:
            render_table(bear, BUY_COLS, "buyScore", "bearish puts")

    with st.expander("Glossary"):
        for term, defn in [
            ("DTE", "Days to expiration"),
            ("Premium", "Bid price per share; falls back to last traded price"),
            ("Δ Delta", "Probability of expiring ITM. Selling: aim for 0.12–0.30."),
            ("OTM%", "How far the strike is from the current stock price"),
            ("IV", "Implied volatility — market's expectation of future moves"),
            ("Wkly%", "Premium / Collateral × (7/DTE)"),
            ("Annual%", "Premium / Collateral × (365/DTE) — primary income metric"),
            ("Collateral", "Cash required: 100 shares × strike price"),
            ("Score", "Buy screener: Delta×100 + Volume÷100 + OI÷1000"),
        ]:
            st.markdown(f"**`{term}`** — {defn}")

else:
    st.markdown(
        "<div style='display:flex;flex-direction:column;align-items:center;justify-content:center;"
        "height:65vh;gap:14px;text-align:center;opacity:0.35;'>"
        "<div style='font-size:52px;line-height:1;'>Ω</div>"
        "<div style='font-size:15px;font-weight:600;letter-spacing:-0.01em;'>"
        "Configure your filters, then run a scan</div>"
        "<div style='font-size:12px;'>Results will appear here.</div>"
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    "<div style='text-align:center;font-size:11px;opacity:0.25;margin-top:48px;"
    "padding-top:16px;border-top:1px solid rgba(255,255,255,0.05);'>"
    "For educational purposes only · Not financial advice · "
    "Data from Yahoo Finance may be delayed</div>",
    unsafe_allow_html=True,
)
