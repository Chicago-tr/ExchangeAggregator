from datetime import datetime, timedelta

from dash import dcc, html

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
