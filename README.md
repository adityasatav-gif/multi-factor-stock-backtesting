# Multi-Factor Stock Ranking & Backtesting System

## Overview

This project is a Python-based quantitative investment tool that ranks stocks using three factors: **value, growth, and momentum**.

The system evaluates a 40-stock universe, assigns each stock a composite factor score, selects the top 10 stocks, constructs an equal-weighted portfolio, and backtests the portfolio over multiple 3-month periods. Performance is compared against the S&P 500 benchmark.

## Investment Strategy

The strategy ranks stocks using three factors:

### 1. Value

Value is measured using the **Price-to-Sales (P/S) ratio**.

A lower P/S ratio receives a higher value score because the strategy favors companies with lower market value relative to their revenue.

### 2. Growth

Growth is measured using **year-over-year revenue growth**.

Higher revenue growth receives a higher growth score.

### 3. Momentum

Momentum is measured using the 6-month price return.

Higher recent returns receive a higher momentum score.

## Factor Scoring & Stock Selection

Each factor is converted into a percentile score so that the three factors can be combined on the same scale.

- **Momentum:** higher momentum receives a higher score.
- **Growth:** higher revenue growth receives a higher score.
- **Value:** lower Price-to-Sales receives a higher score.

The three factor scores are then averaged to create a **Composite Score**:

**Composite Score = (Value Score + Momentum Score + Growth Score) / 3**

Stocks are ranked by their Composite Score in descending order.

The strategy selects the **top 10 stocks** from the ranking and assigns each stock an equal portfolio weight.

## Backtesting Methodology

The strategy is evaluated across seven decision dates from January 2024 through July 2025.

For each decision date:

1. The 40-stock universe is analyzed using the three investment factors.
2. Stocks are ranked by their Composite Score.
3. The top 10 stocks are selected.
4. Each selected stock receives an equal portfolio weight.
5. The portfolio is held for approximately 3 months.
6. Individual stock returns are combined using their portfolio weights.
7. The portfolio return is compared with the S&P 500 over the same period.

The backtest uses historical closing prices and does not account for transaction costs, slippage, taxes, or dividends.

## Performance Results

Using an initial investment of **$10,000**, the multi-factor portfolio grew to approximately **$18,926.50**, representing a cumulative return of **89.27%** across the seven backtest periods.

### Portfolio Performance

- **Average 3-month return:** 9.89%
- **Best 3-month return:** 25.00%
- **Worst 3-month return:** -6.73%
- **Cumulative return:** 89.27%
- **Ending value:** $18,926.50

### S&P 500 Comparison

Over the same backtest periods, a $10,000 investment in the S&P 500 grew to approximately **$14,244.57**, representing a cumulative return of **42.45%**.

The portfolio's cumulative return was therefore **46.82 percentage points higher** than the benchmark over this specific backtest period.

These results are historical backtest results and should not be interpreted as a prediction of future performance.

## Risk Metrics

The project measures risk using the standard deviation of the portfolio's 3-month returns and maximum drawdown.

- **3-month return volatility:** 9.35%
- **Maximum drawdown:** -6.73%

### Volatility

Volatility measures how much the portfolio's returns vary across the backtest periods. A higher value indicates greater variation in returns.

### Maximum Drawdown

Maximum drawdown measures the largest decline from a previous portfolio peak during the backtest.

These metrics provide additional context beyond cumulative return by showing the variability and downside experienced by the strategy.

## Performance Visualization

The project generates a performance chart that compares the growth of a hypothetical $10,000 investment in the multi-factor portfolio with the S&P 500 across the backtest periods.

The chart provides a visual comparison of cumulative portfolio value over time.

## Technologies Used

- **Python** for the overall analysis and portfolio calculations
- **pandas** for data manipulation, ranking, calculations, and DataFrames
- **yfinance** for historical stock prices and financial statement data
- **Matplotlib** for performance visualization
- **unittest** for testing core financial calculations

## Project Structure

- `multi_factor_backtest.py` - Main program containing the stock universe, factor calculations, ranking system, portfolio construction, backtesting, performance analysis, and visualization.
- `test_project.py` - Unit tests for core financial calculations and factor-ranking logic.

## Limitations

This project is intended as an educational quantitative investing project rather than a production trading system.

Several limitations affect the backtest:

- **Limited sample size:** The backtest covers seven 3-month periods, which is not enough to draw strong conclusions about long-term performance.
- **Survivorship bias:** The stock universe is based on a selected set of current large-cap companies, so companies that may have left the universe historically are not represented.
- **Point-in-time data:** Revenue and shares data are obtained through Yahoo Finance and are not guaranteed to represent exactly what would have been available to an investor on each historical decision date.
- **Historical P/S approximation:** Historical market capitalization is approximated using the historical stock price and available shares data.
- **No transaction costs:** The backtest does not account for commissions, bid-ask spreads, market impact, or slippage.
- **No dividends:** Returns are calculated using closing prices and therefore do not include dividend payments.
- **Periodic drawdown:** Maximum drawdown is calculated using the portfolio values at the tested periods rather than daily portfolio values.
- **No predictive guarantee:** Historical backtest performance does not guarantee future results.
