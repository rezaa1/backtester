import yfinance as yf
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_auth
import plotly.graph_objects as go

# List of symbols
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']


# Initialize the Dash app
app = dash.Dash(__name__)

# Define the authentication parameters
VALID_USERNAME_PASSWORD_PAIRS = {
    'reza': 'Mr@120'
}

# Use dash_auth to add authentication to the app
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

# Layout of the app
app.layout = html.Div([
    dcc.Dropdown(
        id='symbol-dropdown',
        options=[{'label': symbol, 'value': symbol} for symbol in symbols],
        value='AAPL'
    ),
    dcc.Graph(id='candlestick-chart')
])

# Callback to update the candlestick chart based on the selected symbol
@app.callback(
    Output('candlestick-chart', 'figure'),
    [Input('symbol-dropdown', 'value')]
)
def update_chart(selected_symbol):
    # Fetch historical price data for the selected symbol
    data = yf.download(selected_symbol, start='2023-01-01', progress=False)

    # Create candlestick chart using Plotly
    candlestick_fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close']
    )])

    # Customize the layout of the candlestick chart
    candlestick_fig.update_layout(
        title=f'{selected_symbol} Candlestick Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )

    return candlestick_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

