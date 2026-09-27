import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# =========================
# SETTINGS
# =========================

decision_dates = [
    "2024-01-02",
    "2024-04-01",
    "2024-07-01",
    "2024-10-01",
    "2025-01-02",
    "2025-04-01",
    "2025-07-01"
]

num_holdings = 10


# =========================
# STOCK UNIVERSE
# =========================

sp500_dict = {
    # Technology & Communications
    "MSFT": "Microsoft Corp",
    "AAPL": "Apple Inc",
    "NVDA": "NVIDIA Corp",
    "GOOGL": "Alphabet Inc",
    "META": "Meta Platforms",
    "AVGO": "Broadcom Inc",
    "CSCO": "Cisco Systems",
    "ORCL": "Oracle Corp",
    "ADBE": "Adobe Inc",
    "CRM": "Salesforce Inc",

    # Financials
    "JPM": "JPMorgan Chase & Co",
    "BAC": "Bank of America Corp",
    "WFC": "Wells Fargo & Co",
    "MS": "Morgan Stanley",
    "GS": "Goldman Sachs Group",
    "V": "Visa Inc",
    "MA": "Mastercard Inc",
    "AXP": "American Express Co",

    # Healthcare
    "LLY": "Eli Lilly & Co",
    "UNH": "UnitedHealth Group",
    "JNJ": "Johnson & Johnson",
    "ABBV": "AbbVie Inc",
    "MRK": "Merck & Co",
    "TMO": "Thermo Fisher Scientific",
    "PFE": "Pfizer Inc",

    # Consumer Discretionary & Staples
    "AMZN": "Amazon.com Inc",
    "TSLA": "Tesla Inc",
    "HD": "Home Depot Inc",
    "WMT": "Walmart Inc",
    "COST": "Costco Wholesale",
    "PG": "Procter & Gamble Co",
    "KO": "Coca-Cola Co",
    "PEP": "PepsiCo Inc",

    # Industrials, Energy & Materials
    "GE": "General Electric",
    "CAT": "Caterpillar Inc",
    "HON": "Honeywell International",
    "XOM": "Exxon Mobil Corp",
    "CVX": "Chevron Corp",
    "LIN": "Linde plc",
    "FCX": "Freeport-McMoRan"
}


# =========================
# MOMENTUM
# =========================

def calculate_momentum(symbol, decision_date):

    decision_timestamp = pd.Timestamp(decision_date)

    # Start far enough back to obtain
    # approximately 6 months of trading data.
    price_start = decision_timestamp - pd.DateOffset(months=7)

    ticker = yf.Ticker(symbol)

    history = ticker.history(
        start=price_start,
        end=decision_date
    )

    if len(history) < 125:
        return None

    current_price = history["Close"].iloc[-1]
    six_month_price = history["Close"].iloc[-125]

    momentum = (
        (current_price - six_month_price)
        / six_month_price
    )

    return momentum


# =========================
# BUILD STOCK RANKINGS
# =========================

def build_rankings(decision_date):

    results = []

    decision_timestamp = pd.Timestamp(decision_date)

    for symbol in sp500_dict:

        try:

            ticker = yf.Ticker(symbol)

            # =========================
            # GROWTH: REVENUE GROWTH
            # =========================

            income_statement = ticker.get_income_stmt(
                freq="yearly"
            )

            if "TotalRevenue" not in income_statement.index:
                print(
                    f"Skipping {symbol}: "
                    f"no revenue data"
                )
                continue

            revenue = income_statement.loc[
                "TotalRevenue"
            ].dropna()

            if revenue.empty:
                print(
                    f"Skipping {symbol}: "
                    f"no valid revenue values"
                )
                continue

            if len(revenue) < 2:
                print(f"Skipping {symbol}: not enough revenue data")
                continue

            latest_two_revenues = revenue.iloc[:2]

            latest_revenue = latest_two_revenues.iloc[0]
            previous_revenue = latest_two_revenues.iloc[1]

            if previous_revenue == 0:
                print(
                    f"Skipping {symbol}: "
                    f"previous revenue is zero"
                )
                continue

            # Revenue growth
            revenue_growth = (
                (latest_revenue - previous_revenue)
                / previous_revenue
            )

            # =========================
            # VALUE: PRICE-TO-SALES
            # =========================

            # Get historical stock prices
            # around the decision date.
            price_history = ticker.history(
                start=decision_date,
                end=(
                    decision_timestamp
                    + pd.Timedelta(days=1)
                )
            )

            if price_history.empty:
                print(
                    f"Skipping {symbol}: "
                    f"no price data"
                )
                continue

            historical_price = (
                price_history["Close"].iloc[0]
            )

            # Yahoo provides current shares outstanding.
            # We use this as an approximation for
            # historical market capitalization.
            shares_outstanding = (
                ticker.get_shares_full(
                    start=decision_timestamp
                    - pd.Timedelta(days=30),
                    end=decision_timestamp
                    + pd.Timedelta(days=30)
                )
            )

            if shares_outstanding is None:
                print(
                    f"Skipping {symbol}: "
                    f"no shares data"
                )
                continue

            shares_outstanding = shares_outstanding.dropna()

            if shares_outstanding.empty:
                print(
                    f"Skipping {symbol}: "
                    f"no valid shares data"
                )
                continue

            shares = shares_outstanding.iloc[-1]

            if shares <= 0:
                print(
                    f"Skipping {symbol}: "
                    f"invalid shares data"
                )
                continue

            # Approximate historical market cap
            historical_market_cap = (
                historical_price * shares
            )

            # Price-to-sales ratio
            price_to_sales = (
                historical_market_cap
                / latest_revenue
            )

            if price_to_sales <= 0:
                print(
                    f"Skipping {symbol}: "
                    f"invalid price-to-sales"
                )
                continue

            # =========================
            # MOMENTUM: 6-MONTH RETURN
            # =========================

            momentum = calculate_momentum(
                symbol,
                decision_date
            )

            if momentum is None:
                print(
                    f"Skipping {symbol}: "
                    f"not enough price history"
                )
                continue

            # =========================
            # ADD STOCK TO RESULTS
            # =========================

            results.append({
                "Ticker": symbol,
                "Price_to_Sales": price_to_sales,
                "Momentum": momentum,
                "Revenue_Growth": revenue_growth
            })

        except Exception as error:

            print(
                f"Skipping {symbol}: "
                f"{type(error).__name__}: {error}"
            )

            continue

    # =========================
    # CREATE DATAFRAME
    # =========================

    df = pd.DataFrame(results)

    if df.empty:

        print(
            f"\nNo stocks available for "
            f"{decision_date}"
        )

        return df

    # =========================
    # FACTOR SCORES
    # =========================

    # Higher momentum = better
    df["Momentum_Score"] = (
        df["Momentum"].rank(pct=True)
    )

    # Lower Price-to-Sales = better
    df["Value_Score"] = (
        1 - df["Price_to_Sales"].rank(pct=True)
    )

    # Higher revenue growth = better
    df["Growth_Score"] = (
        df["Revenue_Growth"].rank(pct=True)
    )

    # =========================
    # COMPOSITE SCORE
    # =========================

    df["Composite_Score"] = (
        df["Value_Score"]
        + df["Momentum_Score"]
        + df["Growth_Score"]
    ) / 3

    # =========================
    # FINAL RANK
    # =========================

    df["Rank"] = df["Composite_Score"].rank(
        ascending=False,
        method="first"
    )

    return df.sort_values("Rank")


# =========================
# RUN BACKTEST
# =========================

backtest_results = []
benchmark_results = []

for decision_date in decision_dates:

    print("\n" + "=" * 60)
    print(
        f"Testing decision date: {decision_date}"
    )
    print("=" * 60)

    ranked = build_rankings(decision_date)

    if ranked.empty:
        continue

    # =========================
    # BUILD PORTFOLIO
    # =========================

    portfolio = ranked.head(
        num_holdings
    ).copy()

    portfolio["Weight"] = (
        1 / len(portfolio)
    )

    portfolio_tickers = (
        portfolio["Ticker"].tolist()
    )

    # =========================
    # 3-MONTH HOLDING PERIOD
    # =========================

    backtest_end = (
            pd.Timestamp(decision_date)
            + pd.DateOffset(months=3)
    )

    # Get S&P 500 price data
    benchmark_data = yf.download(
        "^GSPC",
        start=decision_date,
        end=backtest_end,
        auto_adjust=False,
        progress=False
    )

    if benchmark_data.empty:
        print("Skipping benchmark: no S&P 500 data")
        continue

    # Get starting and ending S&P 500 prices
    benchmark_start = (
        benchmark_data["Close"]["^GSPC"].iloc[0]
    )

    benchmark_end = (
        benchmark_data["Close"]["^GSPC"].iloc[-1]
    )

    # Calculate S&P 500 return
    benchmark_return = (
            (benchmark_end - benchmark_start)
            / benchmark_start
    )

    # Get portfolio price data
    price_data = yf.download(
        portfolio_tickers,
        start=decision_date,
        end=backtest_end,
        auto_adjust=False,
        progress=False
    )

    if price_data.empty:
        print(
            "Skipping period: "
            "no portfolio price data"
        )
        continue

        # Save benchmark result
    benchmark_results.append({
        "Decision_Date": decision_date,
        "Benchmark_Return": benchmark_return
    })

    # =========================
    # DISPLAY RANKINGS
    # =========================

    print(
        f"\nTop {num_holdings} stocks:"
    )

    print(
        ranked[
            [
                "Rank",
                "Ticker",
                "Price_to_Sales",
                "Momentum",
                "Revenue_Growth",
                "Composite_Score"
            ]
        ].head(num_holdings).to_string(
            index=False,
            formatters={
                "Rank": "{:.0f}".format,
                "Price_to_Sales": "{:.2f}".format,
                "Momentum": "{:.1%}".format,
                "Revenue_Growth": "{:.1%}".format,
                "Composite_Score": "{:.3f}".format
            }
        )
    )

    # =========================
    # CALCULATE STOCK RETURNS
    # =========================

    start_prices = price_data.iloc[0]
    end_prices = price_data.iloc[-1]

    stock_returns = (
        (end_prices["Close"] - start_prices["Close"])
        / start_prices["Close"]
    )

    # =========================
    # CALCULATE PORTFOLIO RETURN
    # =========================

    portfolio_returns = (
        portfolio.set_index("Ticker")["Weight"]
        * stock_returns
    )

    total_portfolio_return = (
        portfolio_returns.sum()
    )

    # =========================
    # SAVE BACKTEST RESULT
    # =========================

    backtest_results.append({
        "Decision_Date": decision_date,
        "Portfolio_Return": total_portfolio_return
    })

    print(
        f"\nPortfolio return: "
        f"{total_portfolio_return:.2%}"
    )


# =========================
# =========================
# FINAL BACKTEST RESULTS
# =========================

results_df = pd.DataFrame(
    backtest_results
)

benchmark_df = pd.DataFrame(
    benchmark_results
)

comparison_df = pd.merge(
    results_df,
    benchmark_df,
    on="Decision_Date"
)

print("\n" + "=" * 60)
print("PORTFOLIO VS S&P 500")
print("=" * 60)

print(
    comparison_df.to_string(
        index=False,
        formatters={
            "Portfolio_Return": "{:.2%}".format,
            "Benchmark_Return": "{:.2%}".format
        }
    )
)

# =========================
# RETURN DIFFERENCE
# =========================

comparison_df["Return_Difference"] = (
    comparison_df["Portfolio_Return"]
    - comparison_df["Benchmark_Return"]
)

print("\n" + "=" * 60)
print("RETURN DIFFERENCE VS S&P 500")
print("=" * 60)

print(
    comparison_df[
        [
            "Decision_Date",
            "Portfolio_Return",
            "Benchmark_Return",
            "Return_Difference"
        ]
    ].to_string(
        index=False,
        formatters={
            "Portfolio_Return": "{:.2%}".format,
            "Benchmark_Return": "{:.2%}".format,
            "Return_Difference": "{:.2%}".format
        }
    )
)



print("\n" + "=" * 60)
print("S&P 500 BENCHMARK")
print("=" * 60)

print(
    benchmark_df.to_string(
        index=False,
        formatters={
            "Benchmark_Return": "{:.2%}".format
        }
    )
)

print("\n" + "=" * 60)
print("BACKTEST RESULTS")
print("=" * 60)

if results_df.empty:

    print(
        "No successful backtest periods."
    )

else:

    # Calculate performance statistics
    average_return = (
        results_df["Portfolio_Return"].mean()
    )

    best_return = (
        results_df["Portfolio_Return"].max()
    )

    worst_return = (
        results_df["Portfolio_Return"].min()
    )

    # Display the backtest results
    print(
        results_df.to_string(
            index=False,
            formatters={
                "Portfolio_Return": "{:.2%}".format
            }
        )
    )

    # =========================
    # PERFORMANCE SUMMARY
    # =========================

    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)

    print(
        f"Average 3-month return: "
        f"{average_return:.2%}"
    )

    print(
        f"Best 3-month return: "
        f"{best_return:.2%}"
    )

    print(
        f"Worst 3-month return: "
        f"{worst_return:.2%}"
    )

    # =========================
    # CUMULATIVE PERFORMANCE
    # =========================

    starting_value = 10000

    portfolio_values = [starting_value]

    for return_value in results_df["Portfolio_Return"]:
        new_value = (
                portfolio_values[-1]
                * (1 + return_value)
        )
        portfolio_values.append(new_value)

    portfolio_value = portfolio_values[-1]

    total_return = (
            (portfolio_value - starting_value)
            / starting_value
    )

    print("\n" + "=" * 60)
    print("CUMULATIVE PERFORMANCE")
    print("=" * 60)

    print(
        f"Starting value: ${starting_value:,.2f}"
    )

    print(
        f"Ending value: ${portfolio_value:,.2f}"
    )

    print(
        f"Total return: {total_return:.2%}"
    )

    # =========================
    # BENCHMARK PERFORMANCE
    # =========================

    benchmark_values = [starting_value]

    for return_value in comparison_df["Benchmark_Return"]:
        new_value = (
                benchmark_values[-1]
                * (1 + return_value)
        )
        benchmark_values.append(new_value)

    benchmark_value = benchmark_values[-1]

    benchmark_total_return = (
            (benchmark_value - starting_value)
            / starting_value
    )

    print("\n" + "=" * 60)
    print("BENCHMARK PERFORMANCE")
    print("=" * 60)

    print(
        f"Starting value: ${starting_value:,.2f}"
    )

    print(
        f"S&P 500 ending value: "
        f"${benchmark_value:,.2f}"
    )

    print(
        f"S&P 500 total return: "
        f"{benchmark_total_return:.2%}"
    )

    # =========================
    # RISK METRICS
    # =========================

    volatility = (
        results_df["Portfolio_Return"].std()
    )

    portfolio_values = pd.Series(
        portfolio_values
    )

    # Create data for performance chart
    performance_df = pd.DataFrame({
        "Date": ["Starting"] + decision_dates,
        "Portfolio": portfolio_values,
        "S&P 500": benchmark_values
    })

    # Calculate previous portfolio peaks
    running_max = portfolio_values.cummax()

    # Calculate drawdowns
    drawdowns = (
            (portfolio_values - running_max)
            / running_max
    )

    max_drawdown = drawdowns.min()

    print("\n" + "=" * 60)
    print("RISK METRICS")
    print("=" * 60)

    print(
        f"3-month return volatility: "
        f"{volatility:.2%}"
    )

    print(
        f"Maximum drawdown: "
        f"{max_drawdown:.2%}"
    )

    # =========================
    # PERFORMANCE CHART
    # =========================

    plt.figure(figsize=(10, 6))

    plt.plot(
        performance_df["Date"],
        performance_df["Portfolio"],
        label="Multi-Factor Portfolio"
    )

    plt.plot(
        performance_df["Date"],
        performance_df["S&P 500"],
        label="S&P 500"
    )

    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.title("Multi-Factor Portfolio vs S&P 500")
    plt.legend()
    plt.grid(True)

    plt.show()
