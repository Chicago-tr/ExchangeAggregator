import callbacks  # Gets all callbacks
import dash
import dash.dcc as dcc
import dash.html as html
from prices_layout import prices_tab
from regression_layout import regression_tab

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Crypto Analytics"

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

if __name__ == "__main__":
    app.run(debug=True, port=8050)
