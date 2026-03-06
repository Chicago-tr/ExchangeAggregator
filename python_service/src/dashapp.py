import os
from datetime import datetime, timedelta

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
from dotenv import load_dotenv
from plotly.subplots import make_subplots
from sqlalchemy import create_engine

load_dotenv()

db_url = os.getenv("DB_URL")

if db_url:
    engine = create_engine(db_url)
else:
    raise ValueError("No url to database specified")

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Crypto Multi-Exchange Analytics", style={"textAlign": "center"}),
        html.Div(
            [
                html.Label("Symbol:"),
                dcc.Dropdown(
                    id="symbol-dropdown",
                    options=[],  # populated dynamically
                    value="BTC-USD",  # default
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
        # Charts
        dcc.Graph(id="price-spread-chart"),
        dcc.Graph(id="cross-spread-chart"),
        html.Div(id="stats-summary"),
    ]
)


@app.callback(
    [Output("symbol-dropdown", "options"), Output("exchange-dropdown", "options")],
    [Input("symbol-dropdown", "value")],
)
def update_dropdowns(_):

    symbols_df = pd.read_sql(
        """
        SELECT DISTINCT symbol_code
        FROM bars_1m b
        JOIN symbols s ON b.symbol_id = s.id
        ORDER BY symbol_code
    """,
        engine,
    )

    symbols = [
        {"label": row.symbol_code, "value": row.symbol_code}
        for _, row in symbols_df.iterrows()
    ]

    # Get exchanges
    exchanges_df = pd.read_sql(
        "SELECT exchange_name FROM exchanges ORDER BY exchange_name", engine
    )
    exchanges = [
        {"label": row.exchange_name, "value": row.exchange_name}
        for _, row in exchanges_df.iterrows()
    ]

    return symbols, exchanges


print("test")


# Main price/spread chart
@app.callback(
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

    # Build query for selected symbol(s) and date range
    conditions = []
    params = []

    conditions.append("s.symbol_code = %s")
    params.append(symbol)

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
        params=(tuple(params)),
    )

    if df.empty:
        return go.Figure()

    # Dual y-axis subplot
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Price lines
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

    # Spread overlay
    for exch in df["exchange_name"].unique():
        exch_df = df[df["exchange_name"] == exch]
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


# Cross-exchange spread chart
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
        params=(tuple(params)),
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


if __name__ == "__main__":
    app.run(debug=True, port=8050)
