from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dash_table, html
from db import engine
from plotly.subplots import make_subplots
from scipy.optimize import minimize


# Dropdown callback
@callback(
    [
        Output("symbol-dropdown", "options"),
        Output("exchange-dropdown", "options"),
        Output("regression-symbol", "options"),
    ],
    Input("main-tabs", "value"),
)
def update_all_dropdowns(active_tab):
    symbols_df = pd.read_sql(
        "SELECT DISTINCT symbol_code FROM bars_1m b JOIN symbols s ON b.symbol_id = s.id ORDER BY symbol_code",
        engine,
    )
    symbols = [
        {"label": row.symbol_code, "value": row.symbol_code}
        for _, row in symbols_df.iterrows()
    ]

    exchanges_df = pd.read_sql(
        "SELECT exchange_name FROM exchanges ORDER BY exchange_name", engine
    )
    exchanges = [
        {"label": row.exchange_name, "value": row.exchange_name}
        for _, row in exchanges_df.iterrows()
    ]

    return symbols, exchanges, symbols


# Price spread callback
@callback(
    Output("price-spread-chart", "figure"),
    [
        Input("symbol-dropdown", "value"),
        Input("exchange-dropdown", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_price_spread_chart(symbol, exchanges, start_date, end_date):
    if not symbol:
        return go.Figure()

    conditions = ["s.symbol_code = %s", "b.bar_ts >= %s", "b.bar_ts <= %s"]
    params = [symbol, start_date, end_date]

    if exchanges:
        placeholders = ",".join(["%s"] * len(exchanges))
        conditions.append(f"e.exchange_name IN ({placeholders})")
        params.extend(exchanges)

    where_clause = " AND ".join(conditions)

    df = pd.read_sql(
        f"""
        SELECT b.bar_ts, e.exchange_name, b.close_mid, b.avg_rel_spread_bps
        FROM bars_1m b JOIN exchanges e ON b.exchange_id = e.id
        JOIN symbols s ON b.symbol_id = s.id WHERE {where_clause}
        ORDER BY b.bar_ts, e.exchange_name
    """,
        engine,
        params=tuple(params),
    )

    if df.empty:
        return go.Figure()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for exch in df["exchange_name"].unique():
        exch_df = df[df["exchange_name"] == exch]
        fig.add_trace(
            go.Scatter(
                x=exch_df["bar_ts"], y=exch_df["close_mid"], name=f"{exch} Price"
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=exch_df["bar_ts"],
                y=exch_df["avg_rel_spread_bps"],
                name=f"{exch} Spread (bps)",
                line=dict(dash="dot"),
            ),
            secondary_y=True,
        )

    fig.update_layout(
        title=f"{symbol} - Price & Spread by Exchange",
        xaxis_title="Time",
        yaxis_title="Mid Price",
        yaxis2_title="Spread (bps)",
    )
    return fig


# Cross spread callback
@callback(
    Output("cross-spread-chart", "figure"),
    [
        Input("symbol-dropdown", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_cross_spread_chart(symbol, start_date, end_date):
    if not symbol:
        return go.Figure()

    df = pd.read_sql(
        """
        SELECT bar_ts, cross_spread_bps FROM cross_ex_spread_1m c
        JOIN symbols s ON c.symbol_id = s.id
        WHERE s.symbol_code = %s AND bar_ts >= %s AND bar_ts <= %s ORDER BY bar_ts
    """,
        engine,
        params=(symbol, start_date, end_date),
    )

    if df.empty:
        return go.Figure()
    # Converting from UTC to CDT time
    bar_ts_series = pd.to_datetime(df["bar_ts"])
    if bar_ts_series.dt.tz is None:
        df["bar_ts"] = bar_ts_series.dt.tz_localize("UTC").dt.tz_convert(
            "America/Chicago"
        )
    else:
        df["bar_ts"] = bar_ts_series.dt.tz_convert("America/Chicago")
    fig = px.line(
        df,
        x="bar_ts",
        y="cross_spread_bps",
        title=f"{symbol} - Cross-Exchange Spread (bps)",
    )
    fig.update_yaxes(title="Cross Spread (bps)")
    return fig


# Regression callback
@callback(
    [
        Output("regression-residuals", "figure"),
        Output("regression-zscore", "figure"),
        Output("regression-stats", "children", allow_duplicate=True),
    ],
    [Input("regression-symbol", "value"), Input("regression-time-hours", "value")],
    prevent_initial_call=True,
)
def update_regression_analysis(symbol, hours):
    if not symbol:
        empty_fig = go.Figure().add_annotation(text="Select symbol", showarrow=False)
        return empty_fig, empty_fig, html.Div("Select symbol")

    query = """
    SELECT c.bar_ts, e1.exchange_name as target_exchange, e2.exchange_name as ref_exchange,
           c.regression_residual_bps, c.residual
    FROM cross_ex_regression c JOIN symbols s ON c.symbol_id = s.id
    JOIN exchanges e1 ON c.target_exchange_id = e1.id JOIN exchanges e2 ON c.ref_exchange_id = e2.id
    WHERE s.symbol_code = %s AND (
        (%s = 1 AND c.bar_ts > NOW() - INTERVAL '1 HOUR') OR
        (%s = 4 AND c.bar_ts > NOW() - INTERVAL '4 HOURS') OR
        (%s = 24 AND c.bar_ts > NOW() - INTERVAL '24 HOURS')
    ) ORDER BY c.bar_ts DESC LIMIT 5000
    """

    try:
        df = pd.read_sql(query, engine, params=(symbol, hours, hours, hours))

        bar_ts_series = pd.to_datetime(df["bar_ts"])
        if bar_ts_series.dt.tz is None:
            df["bar_ts"] = bar_ts_series.dt.tz_localize("UTC").dt.tz_convert(
                "America/Chicago"
            )
        else:
            df["bar_ts"] = bar_ts_series.dt.tz_convert("America/Chicago")
    except Exception:
        empty_fig = go.Figure().add_annotation(text="Query error", showarrow=False)
        return empty_fig, empty_fig, html.Div("Error")

    if df.empty:
        empty_fig = go.Figure().add_annotation(text="No data", showarrow=False)
        return empty_fig, empty_fig, html.Div("No data")

    fig_residuals = px.line(
        df,
        x="bar_ts",
        y="regression_residual_bps",
        color="target_exchange",
        title=f"{symbol} Residuals ({hours}h)",
    )
    fig_residuals.add_hline(y=0, line_dash="dash", line_color="red")

    df["z_score"] = (
        df["regression_residual_bps"] - df["regression_residual_bps"].mean()
    ) / df["regression_residual_bps"].std()
    fig_zscore = px.line(
        df,
        x="bar_ts",
        y="z_score",
        color="target_exchange",
        title=f"{symbol} Spread Z-Score ({hours}h)",
    )
    fig_zscore.add_hline(y=2, line_dash="dash", line_color="red")
    fig_zscore.add_hline(y=-2, line_dash="dash", line_color="red")

    stats = (
        df.groupby(["target_exchange", "ref_exchange"])
        .agg({"regression_residual_bps": ["mean", "std"]})
        .round(3)
        .reset_index()
    )
    stats.columns = ["Target", "Reference", "Resid. Mean", "Resid. StdDev"]
    stats_table = dash_table.DataTable(
        data=stats.to_dict("records"),
        columns=[{"name": i, "id": i} for i in stats.columns],
        style_cell={"textAlign": "left", "padding": "12px"},
        style_data={"backgroundColor": "#f8f9fa"},
        style_header={"backgroundColor": "#e9ecef", "fontWeight": "bold"},
        style_table={"overflowX": "auto", "marginTop": "10px"},
    )

    return fig_residuals, fig_zscore, stats_table


@callback(
    [Output("volatility-forecast", "figure"), Output("garch-stats", "children")],
    [
        Input("regression-symbol", "value"),
        Input("regression-time-hours", "value"),
        State("regression-symbol", "value"),
    ],  # ← Unique state trigger
    prevent_initial_call=True,
)
def garch_volatility_forecast(symbol, hours, symbol_state):
    if not symbol:
        empty_fig = go.Figure().add_annotation(text="Select symbol", showarrow=False)
        return empty_fig, html.Div()

    # omega = calibrated_params["omega"]
    # alpha = calibrated_params["alpha"]
    # beta = calibrated_params["beta"]

    query = """
    SELECT c.bar_ts, AVG(c.regression_residual_bps) as residual_bps
    FROM cross_ex_regression c JOIN symbols s ON c.symbol_id = s.id
    WHERE s.symbol_code = %s AND (
        (%s = 1 AND c.bar_ts > NOW() - INTERVAL '1 HOUR') OR
        (%s = 4 AND c.bar_ts > NOW() - INTERVAL '4 HOURS') OR
        (%s = 24 AND c.bar_ts > NOW() - INTERVAL '24 HOURS')
    )
    GROUP BY c.bar_ts ORDER BY c.bar_ts ASC LIMIT 1000
    """

    df = pd.read_sql(query, engine, params=(symbol, hours, hours, hours))

    if df.empty or len(df) < 50:
        return go.Figure().add_annotation(text="Insufficient data"), html.Div()
    bar_ts_series = pd.to_datetime(df["bar_ts"])
    if bar_ts_series.dt.tz is None:
        df["bar_ts"] = bar_ts_series.dt.tz_localize("UTC").dt.tz_convert(
            "America/Chicago"
        )
    else:
        df["bar_ts"] = bar_ts_series.dt.tz_convert("America/Chicago")
    # Raw volatility (%)
    df["residual_bps"] = df["residual_bps"].abs()
    df["returns"] = np.log(df["residual_bps"] / df["residual_bps"].shift(1)).fillna(0)
    df["realized_vol"] = df["returns"].rolling(20, min_periods=5).std() * 100
    # This is the volatility of spread changes
    df["realized_vol"] = df["realized_vol"].fillna(df["realized_vol"].mean())

    if symbol in calibrated_params:
        omega = calibrated_params[symbol]["omega"]
        alpha = calibrated_params[symbol]["alpha"]
        beta = calibrated_params[symbol]["beta"]
        status = " (Calibrated)"
    else:
        # Defaults if calibration not done
        omega = 0.0005 * (df["realized_vol"].tail(50) ** 2).mean() / 10000
        alpha = 0.12
        beta = 0.82
        status = " (Manual)"

    current_vol_sq = (df["realized_vol"].iloc[-1] / 100) ** 2
    current_shock_sq = df["returns"].iloc[-1] ** 2

    forecast_vol = []
    vol_sq = current_vol_sq

    for i in range(24):
        if i == 0:
            vol_sq = omega + alpha * current_shock_sq + beta * current_vol_sq
        else:
            vol_sq = omega + alpha * vol_sq + beta * vol_sq

        if vol_sq <= 0 or np.isnan(vol_sq):
            forecast_vol.append(np.nan)
        else:
            forecast_vol.append(np.sqrt(vol_sq) * 100)

    forecast_times = pd.date_range(start=df["bar_ts"].iloc[-1], periods=24, freq="h")

    persistence = alpha + beta
    denom = 1 - persistence

    if denom <= 0 or np.isnan(denom) or omega <= 0 or np.isnan(omega):
        long_run_vol = np.nan
    else:
        long_run_vol = np.sqrt(omega / denom) * 100

    current_vol = df["realized_vol"].iloc[-1]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["bar_ts"],
            y=df["realized_vol"],
            mode="lines",
            name="Realized Vol (%) (20 period lookback)",
            line=dict(color="blue", width=2),
            connectgaps=True,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast_times,
            y=forecast_vol,
            mode="lines",
            name="GARCH(1,1) Forecast",
            line=dict(color="red", width=2, dash="dash"),
        )
    )

    fig.update_layout(
        title=f"{symbol} Residual Spread Volatility & GARCH(1,1) Forecast",
        yaxis_title="Volatility (%)",
        hovermode="x unified",
    )

    current_time = datetime.now().strftime("%H:%M:%S")
    current_vol = df["realized_vol"].iloc[-1]
    h1_forecast = forecast_vol[0]
    h24_forecast = forecast_vol[-1]

    h1_dir = "↗ UP" if h1_forecast > current_vol else "↘ DOWN"
    h24_dir = "↗ UP" if h24_forecast > current_vol else "↘ DOWN"

    # Check if calibrated or manual
    status = "(Calibrated)" if symbol in calibrated_params else "(Manual)"

    garch_stats = {
        "Metric": [
            "Updated",
            "Current Vol",
            "H1 Forecast",
            "H24 Forecast",
            "Parameters",
            "Persistence",
        ],
        "Value": [
            current_time,
            f"{current_vol:.1f}%",
            f"{h1_forecast:.1f}% {h1_dir}",
            f"{h24_forecast:.1f}% {h24_dir}",
            status,
            f"{alpha + beta:.3f}",
        ],
    }

    stats = dash_table.DataTable(
        data=[
            {"Metric": row[0], "Value": row[1]}
            for row in zip(garch_stats["Metric"], garch_stats["Value"])
        ],
        columns=[{"name": i, "id": i} for i in ["Metric", "Value"]],
        style_cell={"textAlign": "left", "padding": "12px"},
        style_data={"backgroundColor": "#f8f9fa"},
        style_header={"backgroundColor": "#e9ecef", "fontWeight": "bold"},
        style_table={"overflowX": "auto", "marginTop": "10px"},
    )

    return fig, stats


# Store calibrated parameters globally (across callbacks)
calibrated_params = {}


def garch_log_likelihood(params, returns):

    omega, alpha, beta = params
    T = len(returns)
    sigma2 = np.zeros(T)

    # Unconditional variance to initialize
    sigma2[0] = omega / (1 - alpha - beta) if (alpha + beta) < 1 else 0.01

    # GARCH recursion
    for t in range(1, T):
        sigma2[t] = omega + alpha * returns[t - 1] ** 2 + beta * sigma2[t - 1]
        sigma2[t] = max(sigma2[t], 0.0001)  # Floor variance

    # Log-likelihood (negative for minimization)
    nll = 0.5 * np.sum(np.log(2 * np.pi * sigma2) + (returns**2 / sigma2))
    return nll if np.isfinite(nll) else 1e10


@callback(
    Output("garch-calibration-status", "children"),
    Input("calibrate-garch-btn", "n_clicks"),
    [State("regression-symbol", "value"), State("regression-time-hours", "value")],
)
def calibrate_garch(n_clicks, symbol, hours):
    if n_clicks is None or not symbol:
        return ""

    query = """
    SELECT c.bar_ts, AVG(regression_residual_bps) as residual_bps
    FROM cross_ex_regression c JOIN symbols s ON c.symbol_id = s.id
    WHERE s.symbol_code = %s AND (
        (%s = 1 AND bar_ts > NOW() - INTERVAL '1 HOUR') OR
        (%s = 4 AND bar_ts > NOW() - INTERVAL '4 HOURS') OR
        (%s = 24 AND bar_ts > NOW() - INTERVAL '24 HOURS')
    )
    GROUP BY bar_ts ORDER BY bar_ts ASC LIMIT 500
    """

    df = pd.read_sql(query, engine, params=(symbol, hours, hours, hours))

    if len(df) < 50:
        return html.Div("Insufficient data", style={"color": "red"})

    # Log returns
    df["returns"] = np.log(
        (df["residual_bps"].abs() + 1e-6) / (df["residual_bps"].abs().shift(1) + 1e-6)
    ).fillna(0)
    returns = df["returns"].values

    initial_params = [0.0001, 0.1, 0.8]
    result = minimize(
        garch_log_likelihood,
        initial_params,
        args=(returns,),
        bounds=[(1e-6, None), (0, 0.3), (0, 0.95)],
        method="L-BFGS-B",
    )

    if result.success:
        calibrated_params[symbol] = {
            "omega": result.x[0],
            "alpha": result.x[1],
            "beta": result.x[2],
        }
        return html.Div(
            [
                html.P(
                    f"✓ {symbol}: α={result.x[1]:.3f}, β={result.x[2]:.3f}",
                    style={"color": "green", "fontWeight": "bold"},
                )
            ],
            style={
                "padding": "10px",
                "backgroundColor": "#d4edda",
                "borderRadius": "4px",
            },
        )
    else:
        return html.Div("Calibration failed", style={"color": "red"})
