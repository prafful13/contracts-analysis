
# Options Contract Analysis

This document outlines the process used to analyze options contracts in this application.

## Data Source

We use the `yfinance` Python library to fetch options chain data for a given stock ticker. This provides real-time information, which is crucial for making informed decisions.

## Key Data Points

From the options chain, we extract the following key data points for both call and put options:

*   **`strike`**: The price at which the option can be exercised.
*   **`lastPrice`**: The most recent price at which the option was traded.
*   **`bid`**: The highest price a buyer is willing to pay.
*   **`ask`**: The lowest price a seller is willing to accept.
*   **`volume`**: The number of contracts traded during the current day.
*   **`openInterest`**: The total number of outstanding contracts.
*   **`impliedVolatility`**: The market's expectation of the future volatility.

## The "Greeks"

To provide a deeper analysis of the options contracts, we calculate the "Greeks," which measure the sensitivity of an option's price to various factors. We use the `py_vollib` library for these calculations.

The Greeks we calculate are:

*   **Delta (Δ)**: Measures the rate of change of the option's price for a $1 change in the underlying asset's price.
*   **Theta (Θ)**: Represents the rate of time decay of an option's price. This is a crucial metric for options sellers, as you profit from the passage of time.
*   **Vega (ν)**: Indicates the amount an option's price changes for a 1% change in the implied volatility of the underlying stock.
*   **Gamma (Γ)**: Measures the rate of change in an option's delta for a $1 change in the underlying stock price.

## Greeks for Sellers

When selling options (both calls and puts), the interpretations of the Greeks are as follows:

*   **Delta (Δ)**: For a seller, a negative delta is desirable for calls (as you want the stock price to go down or stay the same), and a positive delta is desirable for puts (as you want the stock price to go up or stay the same).
*   **Theta (Θ)**: Theta is the seller's best friend. It represents the time decay of the option. As time passes, the value of the option decreases, which is profitable for the seller.
*   **Vega (ν)**: Vega represents the sensitivity to volatility. Sellers of options benefit from decreasing volatility, as it lowers the option's premium.
*   **Gamma (Γ)**: Gamma is the enemy of the option seller. It represents the rate of change of delta. High gamma means that the delta of the option will change rapidly with the underlying stock price, increasing the seller's risk.

## API

The backend exposes an `/analyze` endpoint that takes a stock ticker as input. This endpoint returns a JSON object containing the options chain data and the calculated Greeks for both puts and calls.
