import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from scanner import StockScanner  # Import your scanner class
#from backtester import BackTester  # Import your backtester class
import yfinance as yf
import plotly.graph_objects as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

VALID_USERNAME_PASSWORD_PAIRS = {
    'user1': 'password1',
    'user2': 'password2',
    'user3': 'password3'
}

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

login_layout = html.Div([
    html.H1('Login'),
    html.Div([
        dcc.Input(id='username-input', placeholder='Username', type='text', style={'marginRight': '10px'}),
        dcc.Input(id='password-input', placeholder='Password', type='password', style={'marginRight': '10px'}),
        html.Button('Login', id='login-button', n_clicks=0)
    ], style={'marginBottom': '20px'}),
    html.Div(id='login-result')
])

main_layout = html.Div([
    dcc.Dropdown(id='symbol-dropdown', options=[], placeholder='Select a symbol'),
    html.Button('Scan', id='scan-button', n_clicks=0),
    dcc.Graph(id='candlestick-graph'),
    html.Div(id='backtest-result')
])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'),
              State('username-input', 'value'),
              State('password-input', 'value'),
              prevent_initial_call=True)
def display_page(pathname, username, password):
    if pathname == '/':
        if username in VALID_USERNAME_PASSWORD_PAIRS and password == VALID_USERNAME_PASSWORD_PAIRS[username]:
            return dcc.Location(pathname='/main', id='dummy')
        else:
            return html.Div('Invalid credentials')
    elif pathname == '/main':
        return main_layout

@app.callback(Output('symbol-dropdown', 'options'),
              Input('scan-button', 'n_clicks'),
              State('symbol-dropdown', 'options'),
              State('symbol-dropdown', 'value'))
def scan_symbols(n_clicks, existing_options, selected_symbol):
    if n_clicks > 0:
        # Replace this with your scanner logic
        symbols_with_signals = ["AAPL", "GOOGL", "MSFT"]  # Example list of symbols with signals
        new_options = [{'label': symbol, 'value': symbol} for symbol in symbols_with_signals]
        return new_options
    return existing_options

@app.callback(Output('candlestick-graph', 'figure'),
              Input('symbol-dropdown', 'value'))
def display_candlestick_chart(selected_symbol):
    if selected_symbol:
        # Replace this with your candlestick chart logic
        spy = yf.download(selected_symbol, start='2023-01-01', progress=False)
        fig = go.Figure(data=[go.Candlestick(
            x=spy.index,
            open=spy['Open'],
            high=spy['High'],
            low=spy['Low'],
            close=spy['Close']
        )])
        return fig

@app.callback(Output('backtest-result', 'children'),
              Input('symbol-dropdown', 'value'))
def display_backtest_result(selected_symbol):
    if selected_symbol:
        # Replace this with your backtester logic
        #backtester = BackTester()
        #result = backtester.run_backtest(selected_symbol)
        result = {"test": "success"}
        return html.Div(f'Backtest Result: {result}')

if __name__ == '__main__':
    app.run_server(debug=True)
