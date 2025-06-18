import requests
import pandas as pd
import streamlit as st
import datetime
from datetime import timedelta, datetime 

# API_KEY = st.secrets["api"]["iex_key"]
API_KEY_ALPHA = st.secrets["alpha_vantage_api"]
API_KEY_POLYGON = st.secrets["polygon_api"]


class StockDataHandler:
    def __init__(self):
        self.api_key_alpha = API_KEY_ALPHA
        self.api_key_polygon = API_KEY_POLYGON

    def get_news(self,symbol, limit=100):
        API_KEY = "lYJmcjOeGqc8BE3hw3wxTQGgJ7d2i0Zn"
        url = f"https://api.polygon.io/v2/reference/news?ticker={symbol}&limit={limit}&apiKey={API_KEY}"
        #print(url)
        response = requests.get(url)
        data = response.json()
        #print(data)

        # df=pd.read_json(response.json)
        # print(df.head)

        if "results" in data:
            articles = data["results"]
         #   print(articles)
            ret=[{
                "Title": article.get("title"),
                "Publisher": article.get("publisher", {}).get("name", ""),
                "Published UTC": article.get("published_utc"),
                "URL": article.get("article_url"),
                "sentiment": article.get("insights", [])[0].get("sentiment", {}),
                "sentiment_reason": article.get("insights", [])[0].get("sentiment_reasoning", {})

            } for article in articles]

            df = pd.DataFrame(ret)
            return df
        else:
            return pd.DataFrame()

    def get_intraday_data_alpha(self,symbol):
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={self.api_key_polygon}"
        response = requests.get(url)
        
        if response.status_code != 200:
            st.error(f"Error fetching data for {symbol}")
            return None
        
        data = response.json()
        time_series_key = "Time Series (5min)"
        
        if time_series_key not in data:
            st.error(f"No data found for {symbol}. Check the ticker or API limits.")
            return None

        # Convert JSON data to DataFrame
        df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
        
        # Rename columns
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        })
        
        df.index = pd.to_datetime(df.index)  # Convert index to datetime
        df = df.sort_index()  # Ensure chronological order
        
        return df
    

    def get_us_tickers(self):
        df1 = pd.read_json("merged_tickers.json")
        df1 = pd.json_normalize(df1['data'])
        
        # Create the search_string column
        df1["search_string"] = (
        df1["ticker"] + " - " + df1["name"] + "\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0" + " - " + df1["primary_exchange"]
    )
        return df1.set_index("ticker")

    def get_daily_data_polygon(self,symbol):
        # 🔹 Your Polygon.io API Key
        API_KEY = self.api_key_polygon  # Replace with your actual API key

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
            return df
            