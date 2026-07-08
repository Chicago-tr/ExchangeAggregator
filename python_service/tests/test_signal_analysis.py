import numpy as np
import pandas as pd

from signal_analysis import (
    backtest_signal,
    compute_signal_positions,
    compute_stationarity_stats,
    split_train_test,
    summarize_backtest,
)


def make_df(residuals, beta=1.0, target_price=60000.0, ref_price=60000.0):
    n = len(residuals)
    return pd.DataFrame(
        {
            "bar_ts": pd.date_range("2026-01-01", periods=n, freq="min"),
            "regression_residual_bps": list(residuals),
            "regression_beta": [beta] * n,
            "target_price": [target_price] * n,
            "ref_price": [ref_price] * n,
            "pair_label": ["Binance vs Coinbase"] * n,
        }
    )


class TestComputeSignalPositions:
    def test_no_trade_below_threshold(self):
        df = make_df([0, 0.5, -0.5, 1.0, -1.0])
        result = compute_signal_positions(df, entry_bps=2.0, exit_bps=1.0)
        assert (result["signal"] == 0).all()

    def test_long_entry_on_negative_residual(self):
        df = make_df([0, -3, -3, -3])
        result = compute_signal_positions(df, entry_bps=2.0, exit_bps=1.0)
        assert result["signal"].iloc[1] == 1
        assert result["signal"].iloc[2] == 1

    def test_short_entry_on_positive_residual(self):
        df = make_df([0, 3, 3, 3])
        result = compute_signal_positions(df, entry_bps=2.0, exit_bps=1.0)
        assert result["signal"].iloc[1] == -1

    def test_exit_on_reversion(self):
        df = make_df([0, 3, 3, 0.5, 0.5])
        result = compute_signal_positions(df, entry_bps=2.0, exit_bps=1.0)
        assert result["signal"].iloc[1] == -1
        assert result["signal"].iloc[3] == 0

    def test_no_lookahead_bias(self):
        # Only the last residual differs between the two series; every earlier
        # signal decision must be identical since the signal only looks backward.
        df1 = make_df([0, 3, 3, 3, 0])
        df2 = make_df([0, 3, 3, 3, 10])
        r1 = compute_signal_positions(df1, entry_bps=2.0, exit_bps=1.0)
        r2 = compute_signal_positions(df2, entry_bps=2.0, exit_bps=1.0)
        assert (r1["signal"].iloc[:4] == r2["signal"].iloc[:4]).all()


class TestBacktestSignal:
    def test_empty_df_returns_empty(self):
        result = backtest_signal(pd.DataFrame())
        assert result.empty

    def test_flat_prices_zero_pnl(self):
        df = make_df([0, 3, 3, 0.5, 0.5], target_price=60000.0, ref_price=60000.0)
        result = backtest_signal(df, entry_bps=2.0, exit_bps=1.0, cost_bps=0.0, notional_usd=10000.0)
        assert np.allclose(result["pnl_bps"].fillna(0), 0.0)

    def test_pnl_direction_long(self):
        # Long spread should profit when the target price rises relative to the ref price.
        df = make_df([0, -3, -3, -3, -3])
        df["target_price"] = [100.0, 100.0, 100.0, 101.0, 101.0]
        df["ref_price"] = [100.0, 100.0, 100.0, 100.0, 100.0]
        result = backtest_signal(df, entry_bps=2.0, exit_bps=1.0, cost_bps=0.0, notional_usd=10000.0)
        assert result.loc[2, "pnl_bps"] > 0

    def test_transaction_costs_reduce_pnl(self):
        df = make_df([0, 3, 3, 0.5, 0.5])
        no_cost = backtest_signal(df.copy(), entry_bps=2.0, exit_bps=1.0, cost_bps=0.0)
        with_cost = backtest_signal(df.copy(), entry_bps=2.0, exit_bps=1.0, cost_bps=1.0)
        assert with_cost["cum_pnl_bps"].iloc[-1] <= no_cost["cum_pnl_bps"].iloc[-1]

    def test_notional_scales_dollar_pnl(self):
        df = make_df([0, 3, 3, 0.5, 0.5])
        df["target_price"] = [100.0, 100.0, 100.0, 101.0, 101.0]
        result = backtest_signal(df, entry_bps=2.0, exit_bps=1.0, cost_bps=0.0, notional_usd=20000.0)
        assert np.allclose(result["pnl_usd"], result["pnl_bps"] / 10000 * 20000)


class TestSummarizeBacktest:
    def test_empty_df(self):
        stats = summarize_backtest(pd.DataFrame())
        assert stats["num_trades"] == 0
        assert stats["sharpe"] == 0.0

    def test_zero_variance_sharpe_is_zero(self):
        df = make_df([0, 0, 0, 0, 0])
        result = backtest_signal(df, entry_bps=2.0, exit_bps=1.0)
        stats = summarize_backtest(result)
        assert stats["sharpe"] == 0.0

    def test_win_rate_between_0_and_100(self):
        df = make_df([0, 3, 3, 0.5, -3, -3, 0.5])
        df["target_price"] = [100.0, 100.0, 101.0, 101.0, 101.0, 100.0, 100.0]
        result = backtest_signal(df, entry_bps=2.0, exit_bps=1.0)
        stats = summarize_backtest(result)
        assert 0 <= stats["win_rate"] <= 100


class TestSplitTrainTest:
    def test_split_preserves_order_and_size(self):
        df = make_df(list(range(10)))
        train, test = split_train_test(df, train_frac=0.7)
        assert len(train) + len(test) == len(df)
        assert train["bar_ts"].max() <= test["bar_ts"].min()

    def test_empty_df(self):
        train, test = split_train_test(pd.DataFrame())
        assert train.empty and test.empty


class TestStationarity:
    def test_insufficient_data_returns_none(self):
        df = make_df([0, 1, 2])
        stats = compute_stationarity_stats(df)
        assert stats["adf_pvalue"] is None

    def test_stationary_series_detected(self):
        rng = np.random.default_rng(42)
        n = 300
        residuals = np.zeros(n)
        for i in range(1, n):
            residuals[i] = 0.5 * residuals[i - 1] + rng.normal(0, 1)
        df = make_df(residuals.tolist())
        stats = compute_stationarity_stats(df)
        assert stats["adf_pvalue"] is not None
        assert stats["is_stationary"] is True
        assert stats["half_life_bars"] is not None
        assert stats["half_life_bars"] > 0
