import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_handler.stock_data import StockDataHandler



class StockDashboardApp:
    def __init__(self):
        #self.api_key = st.secrets["api"]["iex_key"]
        #self.api_base_url = "https://cloud.iexapis.com/stable/"
        self.data_handler = StockDataHandler()

    def get_us_tickers(self):
        df1 = pd.read_json("merged_tickers.json")
        df1 = pd.json_normalize(df1['data'])
        
        # Create the search_string column
        df1["search_string"] = (
        df1["ticker"] + " - " + df1["name"] + "\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0" + " - " + df1["primary_exchange"]
    )
        return df1.set_index("ticker")
    def run(self):
        st.set_page_config(page_title="Stock Dashboard", layout="wide", page_icon="📈")
        # auto refresh after a certain interval. turn off because of API limit. 
        # interval = 60000  # in milliseconds
        # st_autorefresh(interval=interval, key='data_refresh')

        st.markdown("<style>.stRadio > div {display: flex; flex-direction: column; gap: 10px; margin-bottom: 10px;}</style>", unsafe_allow_html=True)
        st.sidebar.markdown("# Stock Dashboard")
        st.sidebar.markdown("Please select a stock symbol and duration from the options below to view detailed stock data and charts.")
        us_tickers = self.get_us_tickers()
        popular_symbols = ["AAPL", "GOOGL", "MSFT", "META", "NVDA"]
        new_symbol = st.sidebar.text_input("Input a new ticker:")
    #     selected_stocks = st.multiselect(
    #     "Choose Ticker", us_tickers["search_string"].tolist()
    # )       
        if new_symbol:
            popular_symbols.append(new_symbol.upper())
            st.sidebar.success(f"Added {new_symbol.upper()} to the list")
        #symbol = st.sidebar.selectbox("Select a ticker:", popular_symbols, index=2)
        
        symbol = st.sidebar.multiselect("Select a ticker:", us_tickers["search_string"].tolist(),max_selections = 1,default=["AAPL - Apple Inc.             - XNAS"])
        #st.write(symbol)
        if not symbol:
            st.error("Please select at least one stock.")    
        symbol = symbol[0].split(" - ")[0]

        time_range_options = ["5d","1m", "3m", "6m", "1y", "2y"] #, "5y", "YTD", "max"]
        selected_time_range = st.sidebar.selectbox("Select period:", time_range_options, index=2)

        show_candlestick = st.sidebar.checkbox("Candlestick Chart", value=True)
        show_summary = st.sidebar.checkbox("Summary", value=True)
        # show_moving_averages = st.sidebar.checkbox("Moving Averages", value=False)
        # show_bollinger_bands = st.sidebar.checkbox("Bollinger Bands", value=False)
        # show_obv = st.sidebar.checkbox("On-Balance Volume", value=False)
        # show_rsi = st.sidebar.checkbox("Relative Strength Index (RSI)", value=False)
        # show_macd = st.sidebar.checkbox("Moving Average Convergence Divergence (MACD)", value=False)
        # show_atr = st.sidebar.checkbox("Average True Range (ATR)", value=False)
        # show_vwap = st.sidebar.checkbox("Volume Weighted Average Price (VWAP)", value=False)
        # show_volatility = st.sidebar.checkbox("Historical Volatility", value=False)

if __name__ == "__main__":
    app = StockDashboardApp()
    app.run()
