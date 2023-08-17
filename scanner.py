import os
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime as datetime
def generate_sell_signals(data):
    sell_signals = []
    inside_bar = []

    bar_start = len(data) - 10 - 3 
    if bar_start < 0:
        bar_start = 0
    
    for i in range(bar_start, len(data)):
        # Check for Inside Bar pattern
        if (
            data['High'][i-1] > data['High'][i-2] and
            data['Low'][i-1] < data['Low'][i-2] and
            data['High'][i] <= data['High'][i-1] and
            data['Low'][i] >= data['Low'][i-1]
        ):
            inside_bar_idx = i
            
            # Check for Breakdown Candle(s)
            breakdown_candles = []
            for j in range(i, i+3):
                if data['Close'][j] < data['Low'][i-1]:
                    breakdown_candles.append(j)
            
            if len(breakdown_candles) > 0:
                # Check for Bearish Candle
                bearish_candle_idx = None
                for k in range(breakdown_candles[-1], len(data)):
                    if data['Close'][k] < data['Open'][k]:
                        bearish_candle_idx = k
                        break
                
                if bearish_candle_idx:
                    # Check for the number of candles between Inside Bar and Bearish Candle
                    if bearish_candle_idx - inside_bar_idx <= 6:
                        inside_bar.append(data.index[inside_bar_idx])
                        sell_signals.append(data.index[bearish_candle_idx+1])
    
    return sell_signals,inside_bar

def generate_buy_signals(data):
    buy_signals = []
    inside_bar = []
    bar_start = len(data) - 10 - 3 
    if bar_start < 0:
        bar_start = 0
    
    for i in range(bar_start , len(data)):
        # Check for Inside Bar pattern
        if (
            data['High'][i-1] > data['High'][i-2] and
            data['Low'][i-1] < data['Low'][i-2] and
            data['High'][i] <= data['High'][i-1] and
            data['Low'][i] >= data['Low'][i-1]
        ):
            inside_bar_idx = i
            
            # Check for Breakout Candle(s)
            breakout_candles = []
            for j in range(i, i+3):
                if data['Close'][j] > data['High'][i-1]:
                    breakout_candles.append(j)
           
            
            if len(breakout_candles) > 0:
                # Check for Bullish Candle
                bullish_candle_idx = None
                for k in range(breakout_candles[-1], len(data)):
                    if data['Close'][k] > data['Open'][k]:
                        bullish_candle_idx = k
                        break
                    if k-breakout_candles[-1] > 6:
                        break
                if bullish_candle_idx:
                    # Check for the number of candles between Inside Bar and Bullish Candle
                    if bullish_candle_idx - inside_bar_idx <= 6:
                        inside_bar.append(data.index[inside_bar_idx])
                        buy_signals.append(data.index[bullish_candle_idx+1])
    
    return buy_signals,inside_bar

class StockScanner:
    def __init__(self,history='10d'):
        self.sp500_symbols = self.get_sp500_symbols()
        self.history= history
        
    def get_sp500_symbols(self):
        # Fetch the list of S&P 500 companies' symbols and names
        sp500_df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        sp500_symbols = sp500_df['Symbol'].tolist()
        return sp500_symbols
    def get_fav_symbols(self):
        # Fetch the list of S&P 500 companies' symbols and names
        fav = ['spy','qqq','iwm','dia','cost','baba','aapl','wmt','msft','aapl','tsla','tlt','tgt','jpm','abnb','intc','riot','mara','coin','fivn','bac', 'dis','pfe','ai','pltr','googl','meta','nvda',
              'dis','amc','']
        return fav
    
    def download_data(self, symbol, start_date=None, end_date=None):
        # Download stock price data from Yahoo Finance
        if not start_date:
            start_date = (pd.Timestamp.today() - pd.DateOffset(days=10)).date().strftime('%Y-%m-%d')
        if not end_date:
            end_date = pd.Timestamp.today().date().strftime('%Y-%m-%d')
        #data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        data = yf.download(symbol,  period=self.history, progress=False)
        
        return data

    def generate_buy_signals(self,data):
        buy_signals = []
        buy_signals,a=generate_buy_signals(data)
        return buy_signals

    def generate_sell_signals(self,data):
        sell_signals , a = generate_sell_signals(data)
        return sell_signals

    
    def save_data_to_csv(self, data, symbol):
        # Save the data to a CSV file
        data.to_csv(f'{symbol}.csv')
    
    def load_data_from_csv(self, symbol):
        # Load data from a CSV file
        data = pd.read_csv(f'{symbol}.csv', index_col='Date', parse_dates=True)
        return data
    
    def scan(self, symbol):
        # Load data, generate signals, and plot the chart
        data = self.update_data(symbol)
        buy_signals = self.generate_buy_signals(data)
        sell_signals = self.generate_sell_signals(data)

        return buy_signals,sell_signals
        
    def plot(self,symbol,plot_show=True):

        data = self.update_data(symbol)

        buy_signals = self.generate_buy_signals(data)
        sell_signals = self.generate_sell_signals(data)

        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        )])
        
        fig.add_trace(go.Scatter(
            mode='markers',
            x=buy_signals,
            y=data.loc[buy_signals]['Low'],
            marker=dict(color='green', size=10, symbol='triangle-up'),
            name='Buy Signal'
        ))
        
        fig.add_trace(go.Scatter(
            mode='markers',
            x=sell_signals,
            y=data.loc[sell_signals]['High'],
            marker=dict(color='red', size=10, symbol='triangle-down'),
            name='Sell Signal'
        ))
        
        fig.update_layout(
            title=f'{symbol} Candlestick Chart with Buy and Sell Signals',
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False
        )
        if plot_show:
            fig.show()
        else:
            return fig
        
    def update_data(self, symbol):
        # Load the existing data
        try:
            data = self.load_data_from_csv(symbol)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}; dowloading")
            data = self.download_data(symbol)
            self.save_data_to_csv(data,symbol)
            pass
        
        # Get the last available date in the data
        last_date = data.index[-1]
        
        
        # Get today's date
        ticker = yf.Ticker(symbol)
        last_trading_day = datetime.fromtimestamp(ticker.history_metadata['currentTradingPeriod']['regular']['end']).strftime('%Y-%m-%d')
        
        # Check if data is up-to-date
        if last_date is None or (last_date +  pd.DateOffset(days=1)).strftime('%Y-%m-%d') < last_trading_day:

            # Download the missing data
            missing_data = self.download_data(symbol, start_date=(last_date + pd.DateOffset(days=1)).strftime('%Y-%m-%d'), end_date=last_trading_day)
            
            if not missing_data.empty:
                # Append missing data to existing data
                updated_data = pd.concat([data, missing_data])
                
                # Save the updated data
                self.save_data_to_csv(updated_data, symbol)
                data = updated_data
        return data

    def scan_symbols(self,list='fav'):
        print("scanning ....")
        buy=[]
        sell=[]
        if list == 'fav':
            symbols = self.get_fav_symbols();
        else:
            symbols = self.get_sp500_symbols();
            
        
        for symbol in symbols:
            try:
                buy_signals,sell_signals=self.scan(symbol)
                if buy_signals:
                    buy.append(symbol)
                if sell_signals:
                    sell.append(symbol)
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                pass
        return buy,sell
