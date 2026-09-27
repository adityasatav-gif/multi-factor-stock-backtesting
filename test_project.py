import unittest


class TestCalculations(unittest.TestCase):

    def test_revenue_growth(self):
        latest_revenue = 120
        previous_revenue = 100

        revenue_growth = (
            (latest_revenue - previous_revenue)
            / previous_revenue
        )

        self.assertAlmostEqual(
            revenue_growth,
            0.20
        )

    def test_momentum(self):
        current_price = 120
        six_month_price = 100

        momentum = (
            (current_price - six_month_price)
            / six_month_price
        )

        self.assertAlmostEqual(
            momentum,
            0.20
        )

    def test_portfolio_return(self):
        stock_returns = [0.10, 0.05, -0.02]
        weights = [1 / 3, 1 / 3, 1 / 3]

        portfolio_return = sum(
            return_value * weight
            for return_value, weight
            in zip(stock_returns, weights)
        )

        self.assertAlmostEqual(
            portfolio_return,
            0.0433333333
        )

    def test_factor_ranking(self):
        import pandas as pd

        data = pd.DataFrame({
            "Momentum": [0.10, 0.20, 0.30],
            "Revenue_Growth": [0.05, 0.15, 0.25],
            "Price_to_Sales": [6.0, 4.0, 2.0]
        })

        data["Momentum_Score"] = (
            data["Momentum"].rank(pct=True)
        )

        data["Growth_Score"] = (
            data["Revenue_Growth"].rank(pct=True)
        )

        data["Value_Score"] = (
            1 - data["Price_to_Sales"].rank(pct=True)
        )

        self.assertGreater(
            data["Momentum_Score"].iloc[2],
            data["Momentum_Score"].iloc[0]
        )

        self.assertGreater(
            data["Growth_Score"].iloc[2],
            data["Growth_Score"].iloc[0]
        )

        self.assertGreater(
            data["Value_Score"].iloc[2],
            data["Value_Score"].iloc[0]
        )