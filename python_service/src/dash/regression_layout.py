from dash import dcc, html

# regression_tab = html.Div(
#     [
#         html.Div(
#             [
#                 html.Label("Symbol:"),
#                 dcc.Dropdown(
#                     id="regression-symbol",
#                     options=[],
#                     value=None,
#                     style={"width": "200px"},
#                 ),
#                 html.Label("Time Window:"),
#                 dcc.Dropdown(
#                     id="regression-time-hours",
#                     options=[
#                         {"label": "1 Hour", "value": 1},
#                         {"label": "4 Hours", "value": 4},
#                         {"label": "24 Hours", "value": 24},
#                     ],
#                     value=24,
#                     style={"width": "200px"},
#                 ),
#             ],

#             style={
#                 "padding": "20px",
#                 "backgroundColor": "#f8f9fa",
#                 "marginBottom": "20px",
#             },
#         ),
#         # Residuals + regression stats
#         dcc.Graph(id="regression-residuals"),
#         html.Div(
#             id="regression-stats",
#             style={"padding": "20px", "paddingBottom": "100px"},
#         ),
#         # Z-score
#         dcc.Graph(id="regression-zscore"),
#         dcc.Graph(id="volatility-forecast"),
#         html.Div(id="garch-stats", style={"padding": "20px"}),
#     ],
#     style={"padding": "20px"},
# )

regression_tab = html.Div(
    [
        # Controls section with Calibrate button
        html.Div(
            [
                html.Label("Symbol:"),
                dcc.Dropdown(
                    id="regression-symbol",
                    options=[],
                    value=None,
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
                    style={
                        "width": "200px",
                    },
                ),
                html.Button(
                    "Calibrate GARCH",
                    id="calibrate-garch-btn",
                    style={
                        "padding": "8px 16px",
                        "backgroundColor": "#3498db",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "4px",
                        "cursor": "pointer",
                        "fontSize": "14px",
                        "marginTop": "5px",
                    },
                ),
            ],
            style={
                "padding": "20px",
                "backgroundColor": "#f8f9fa",
                "marginBottom": "10px",
            },
        ),
        # Calibration status
        html.Div(id="garch-calibration-status", style={"padding": "0 20px 15px 20px"}),
        # Residuals chart + stats table
        html.Div(
            [
                dcc.Graph(id="regression-residuals"),
                html.Div(
                    id="regression-stats", style={"padding": "10px 20px 20px 20px"}
                ),
            ],
            style={"marginBottom": "30px"},
        ),
        # Z-score chart (standalone)
        dcc.Graph(id="regression-zscore", style={"marginBottom": "30px"}),
        # Volatility forecast + GARCH stats table
        html.Div(
            [
                dcc.Graph(id="volatility-forecast"),
                html.Div(id="garch-stats", style={"padding": "10px 20px 20px 20px"}),
            ]
        ),
    ],
    style={"padding": "20px"},
)
