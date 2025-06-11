import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from datetime import datetime,timedelta
import requests
import json

from data_handler.stock_data import StockDataHandler
from visualizer.plots import StockVisualizer
from fin_metrics.calculator import StockMetricsCalculator


class StockDashboardApp:
    def __init__(self):
        #self.api_key = st.secrets["api"]["iex_key"]
        #self.api_base_url = "https://cloud.iexapis.com/stable/"
        self.data_handler = StockDataHandler()
        self.visualizer = StockVisualizer()
        self.calculator = StockMetricsCalculator()

    def get_us_tickers(self):
        df1 = pd.read_json("merged_tickers.json")
        df1 = pd.json_normalize(df1['data'])
        
        # Create the search_string column
        df1["search_string"] = (
        df1["ticker"] + " - " + df1["name"] + "\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0" + " - " + df1["primary_exchange"]
    )
        return df1.set_index("ticker")
    
    def get_daily_data(self,symbol):
        # 🔹 Your Polygon.io API Key
        API_KEY = self.data_handler.api_key_polygon

        # 🔹 Define Date Range (Last 5 Years)
        end_date = datetime.today().strftime('%Y-%m-%d')  # Today's date
        start_date = (datetime.today() - timedelta(days=5*365)).strftime('%Y-%m-%d')  # 5 years ago
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}?adjusted=true&sort=asc&limit=5000&apiKey={API_KEY}"

        # 🔹 Fetch Data
        response = requests.get(url)
        data = response.json()

        # 🔹 Process Data
        if "results" in data:
            df = pd.DataFrame(data["results"])
            
            # Convert timestamp to readable date
            df["date"] = pd.to_datetime(df["t"], unit="ms")
            
            # Select relevant columns
            df = df[["date", "o", "h", "l", "c", "v"]]
            
            # Rename columns
            df.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
            df.set_index('Date', inplace=True)
            print(df.head())
            return df

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
        print(symbol)    
        symbol = symbol[0].split(" - ")[0]
        print(symbol)
        time_range_options = ["5d","1m", "3m", "6m", "1y", "2y"] #, "5y", "YTD", "max"]
        selected_time_range = st.sidebar.selectbox("Select period:", time_range_options, index=2)

        show_candlestick = st.sidebar.checkbox("Candlestick Chart", value=True)
        show_summary = st.sidebar.checkbox("Summary", value=True)
        show_moving_averages = st.sidebar.checkbox("Moving Averages", value=False)
        show_bollinger_bands = st.sidebar.checkbox("Bollinger Bands", value=False)
        show_obv = st.sidebar.checkbox("On-Balance Volume", value=False)
        show_rsi = st.sidebar.checkbox("Relative Strength Index (RSI)", value=False)
        show_macd = st.sidebar.checkbox("Moving Average Convergence Divergence (MACD)", value=False)
        show_atr = st.sidebar.checkbox("Average True Range (ATR)", value=False)
        show_vwap = st.sidebar.checkbox("Volume Weighted Average Price (VWAP)", value=False)
        show_volatility = st.sidebar.checkbox("Historical Volatility", value=False)



        if symbol:
            print(symbol)
            stock_data= self.get_daily_data(symbol)
        

            
        if stock_data is not None:
            price_difference, percentage_difference = self.calculator.calculate_price_difference(stock_data)
            latest_close_price = float(stock_data.iloc[-1]["Close"])
            max_52_week_high = float(stock_data["High"].max())
            min_52_week_low = float(stock_data["Low"].min())
            

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Close Price", f"${latest_close_price:.2f}")
            with col2:
                st.metric("Price Difference", f"${price_difference:.2f}", f"{percentage_difference:+.2f}%")
            with col3:
                st.metric("52-Week High", f"${max_52_week_high:.2f}")
            with col4:
                st.metric("52-Week Low", f"${min_52_week_low:.2f}")

            if show_candlestick:
                candlestick_chart = self.visualizer.plot_candlestick(stock_data, symbol, selected_time_range)
                st.subheader("Candlestick Chart")
                st.plotly_chart(candlestick_chart, use_container_width=True)

            if show_moving_averages:
                stock_data = self.calculator.calculate_moving_averages(stock_data)
                ma_fig = self.visualizer.plot_moving_averages(stock_data)
                st.plotly_chart(ma_fig, use_container_width=True)
            if show_bollinger_bands:
                stock_data = self.calculator.calculate_bollinger_bands(stock_data)
                bb_fig = self.visualizer.plot_bollinger_bands(stock_data)
                st.plotly_chart(bb_fig, use_container_width=True)

            if show_obv:
                stock_data = self.calculator.calculate_on_balance_volume(stock_data)
                obv_fig = self.visualizer.plot_obv(stock_data)
                st.plotly_chart(obv_fig, use_container_width=True)

            if show_rsi:
                stock_data = self.calculator.calculate_rsi(stock_data)
                rsi_fig = self.visualizer.plot_rsi(stock_data)
                st.plotly_chart(rsi_fig, use_container_width=True)

            if show_macd:
                stock_data = self.calculator.calculate_macd(stock_data)
                macd_fig = self.visualizer.plot_macd(stock_data)
                st.plotly_chart(macd_fig, use_container_width=True)

            if show_atr:
                stock_data = self.calculator.calculate_atr(stock_data)
                atr_fig = self.visualizer.plot_atr(stock_data)
                st.plotly_chart(atr_fig, use_container_width=True)

            if show_vwap:
                stock_data = self.calculator.calculate_vwap(stock_data)
                vwap_fig = self.visualizer.plot_vwap(stock_data)
                st.plotly_chart(vwap_fig, use_container_width=True)

            if show_volatility:
                stock_data = self.calculator.calculate_historical_volatility(stock_data)
                vol_fig = self.visualizer.plot_volatility(stock_data)
                st.plotly_chart(vol_fig, use_container_width=True)

            if show_summary:
                st.subheader("Summary")
                st.dataframe(stock_data.tail())

            st.download_button("Download Stock Data Overview", stock_data.to_csv(index=True), file_name=f"{symbol}_stock_data.csv", mime="text/csv")

if __name__ == "__main__":
    app = StockDashboardApp()
    app.run()
