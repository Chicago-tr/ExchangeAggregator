import os
from datetime import datetime, timedelta

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
from dotenv import load_dotenv
from plotly.subplots import make_subplots
from sqlalchemy import create_engine

load_dotenv()


db_url = os.getenv("DB_URL")

if db_url:
    engine = create_engine(db_url)
else:
    raise ValueError("No url to database specified in .env")

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define tab layouts FIRST
prices_tab = html.Div(
    [
        html.Div(
            [
                html.Label("Symbol:"),
                dcc.Dropdown(
                    id="symbol-dropdown",
                    options=[],
                    value="BTC-USD",
                    style={"width": "200px"},
                ),
                html.Label("Date Range:"),
                dcc.DatePickerRange(
                    id="date-range",
                    start_date=datetime.now() - timedelta(days=7),
                    end_date=datetime.now(),
                    style={"width": "250px"},
                ),
                html.Label("Exchanges:"),
                dcc.Dropdown(
                    id="exchange-dropdown", multi=True, style={"width": "300px"}
                ),
            ],
            style={"padding": "20px"},
        ),
        dcc.Graph(id="price-spread-chart"),
        dcc.Graph(id="cross-spread-chart"),
        html.Div(id="stats-summary"),
    ],
    style={"padding": "20px"},
)

regression_tab = html.Div(
    [
        html.Div(
            [
                html.Label("Symbol:"),
                dcc.Dropdown(
                    id="regression-symbol",
                    options=[],
                    value="BTC-USD",
                    style={"width": "200px"},
                ),
                html.Label("Time Window:"),
                dcc.Dropdown(
                    id="regression-time-hours",
                    options=[
                        {"label": "1 Hour", "value": 1},
                        {"label": "4 Hours", "value": 4},
                        {"label": "24 Hours", "value": 24},
                    ],
                    value=24,
                    style={"width": "200px"},
                ),
            ],
            style={
                "padding": "20px",
                "backgroundColor": "#f8f9fa",
                "marginBottom": "20px",
            },
        ),
        dcc.Graph(id="regression-residuals"),
        dcc.Graph(id="regression-zscore"),
        html.Div(
            id="regression-stats", style={"padding": "20px", "paddingBottom": "100px"}
        ),
    ],
    style={"padding": "20px"},
)

app.layout = html.Div(
    [
        html.H1(
            "Crypto Multi-Exchange Analytics",
            style={"textAlign": "center", "marginBottom": "30px"},
        ),
        dcc.Tabs(
            [
                dcc.Tab(label="Price & Spread", value="prices", children=[prices_tab]),
                dcc.Tab(
                    label="Regression Analysis",
                    value="regression",
                    children=[regression_tab],
                ),
            ],
            id="main-tabs",
            value="prices",
        ),
    ]
)


# Unified dropdown callback for ALL dropdowns
@app.callback(
    [
        Output("symbol-dropdown", "options"),
        Output("exchange-dropdown", "options"),
        Output("regression-symbol", "options"),
    ],
    [Input("main-tabs", "value")],
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


# Price/Spread callback (scoped to prices tab)
@app.callback(
    Output("price-spread-chart", "figure"),
    [
        Input("symbol-dropdown", "value"),
        Input("exchange-dropdown", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
# YOUR ORIGINAL PRICE/SPREAD CALLBACK - UNCHANGED

def update_price_spread_chart(symbol, exchanges, start_date, end_date):
    if not symbol:
        return go.Figure()

    conditions = []
    params = []

    conditions.append("s.symbol_code = %s")
    params.append(symbol)

    conditions.append("b.bar_ts >= %s")
    params.append(start_date)
    conditions.append("b.bar_ts <= %s")
    params.append(end_date)

    if exchanges:
        placeholders = ",".join(["%s"] * len(exchanges))
        conditions.append(f"e.exchange_name IN ({placeholders})")
        params.extend(exchanges)

    where_clause = " AND ".join(conditions)

    df = pd.read_sql(
        f"""
            SELECT
                b.bar_ts,
                e.exchange_name as exchange_name,
                b.close_mid,
                b.avg_rel_spread_bps
            FROM bars_1m b
            JOIN exchanges e ON b.exchange_id = e.id
            JOIN symbols s ON b.symbol_id = s.id
            WHERE {where_clause}
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
                x=exch_df["bar_ts"],
                y=exch_df["close_mid"],
                name=f"{exch} Price",
                mode="lines",
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=exch_df["bar_ts"],
                y=exch_df["avg_rel_spread_bps"],
                name=f"{exch} Spread (bps)",
                mode="lines",
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


# YOUR ORIGINAL CROSS-SPREAD CALLBACK - UNCHANGED
@app.callback(
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
    params = [symbol, start_date, end_date]
    df = pd.read_sql(
        """
        SELECT bar_ts, cross_spread_bps
        FROM cross_ex_spread_1m c
        JOIN symbols s ON c.symbol_id = s.id
        WHERE s.symbol_code = %s
        AND bar_ts >= %s
        AND bar_ts <= %s
        ORDER BY bar_ts
    """,
        engine,
        params=tuple(params),
    )

    if df.empty:
        return go.Figure()

    fig = px.line(
        df,
        x="bar_ts",
        y="cross_spread_bps",
        title=f"{symbol} - Cross-Exchange Spread (bps)",
    )

    fig.update_yaxes(title="Cross Spread (bps)")
    return fig


# NEW REGRESSION CALLBACK - Uses YOUR exact table structure
@app.callback(
    [
        Output("regression-residuals", "figure"),
        Output("regression-zscore", "figure"),
        Output("regression-stats", "children"),
    ],
    [Input("regression-symbol", "value"), Input("regression-time-hours", "value")],
)
def update_regression_analysis(symbol, hours):
    if not symbol:
        empty_fig = go.Figure().add_annotation(text="Select symbol", showarrow=False)
        return empty_fig, empty_fig, html.Div("Select symbol")

    # FIXED: Use UNION of fixed intervals - no f-strings, no parameterization issues
    query = """
    SELECT c.bar_ts,
           e1.exchange_name as target_exchange,
           e2.exchange_name as ref_exchange,
           c.regression_residual_bps,
           c.residual
    FROM cross_ex_regression c
    JOIN symbols s ON c.symbol_id = s.id
    JOIN exchanges e1 ON c.target_exchange_id = e1.id
    JOIN exchanges e2 ON c.ref_exchange_id = e2.id
    WHERE s.symbol_code = %s
    AND (
        ({} = 1 AND c.bar_ts > NOW() - INTERVAL '1 HOUR') OR
        ({} = 4 AND c.bar_ts > NOW() - INTERVAL '4 HOURS') OR
        ({} = 24 AND c.bar_ts > NOW() - INTERVAL '24 HOURS')
    )
    ORDER BY c.bar_ts DESC
    LIMIT 5000
    """.format(hours, hours, hours)

    try:
        df = pd.read_sql(query, engine, params=(symbol,))
    except Exception as e:
        empty_fig = go.Figure().add_annotation(text="Query error", showarrow=False)
        return empty_fig, empty_fig, html.Div(f"Error: {str(e)}")

    if df.empty:
        empty_fig = go.Figure().add_annotation(text="No data", showarrow=False)
        return empty_fig, empty_fig, html.Div("No regression data")

    # Residuals chart
    fig_residuals = px.line(
        df,
        x="bar_ts",
        y="regression_residual_bps",
        color="target_exchange",
        title=f"{symbol} Regression Residuals ({hours}h)",
    )
    fig_residuals.add_hline(y=0, line_dash="dash", line_color="red")

    # Z-score chart
    df["z_score"] = (
        df["regression_residual_bps"] - df["regression_residual_bps"].mean()
    ) / df["regression_residual_bps"].std()
    fig_zscore = px.line(
        df,
        x="bar_ts",
        y="z_score",
        color="target_exchange",
        title=f"{symbol} Z-Score Residuals ({hours}h)",
    )
    fig_zscore.add_hline(y=2, line_dash="dash", line_color="red")
    fig_zscore.add_hline(y=-2, line_dash="dash", line_color="red")

    # Simple stats
    stats = (
        df.groupby(["target_exchange", "ref_exchange"])
        .agg({"regression_residual_bps": ["mean", "std"]})
        .round(3)
        .reset_index()
    )
    stats.columns = ["Target", "Reference", "Mean", "StdDev"]

    stats_table = dash_table.DataTable(
        data=stats.to_dict("records"),
        columns=[{"name": i, "id": i} for i in stats.columns],
        style_cell={"textAlign": "left"},
    )

    return fig_residuals, fig_zscore, stats_table


if __name__ == "__main__":
    app.run(debug=True, port=8050)
