import streamlit as st
import pandas as pd
from data_handler.stock_data import StockDataHandler


# You can use session state to keep track of portfolio across interactions
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

data_handler = StockDataHandler()
us_tickers = data_handler.get_us_tickers()
st.title("📊 Portfolio Tracker")
ticker = st.multiselect("Select a ticker:", us_tickers["search_string"].tolist(),max_selections = 1,default=["AAPL - Apple Inc.             - XNAS"])
#st.write(symbol)
if not ticker:
    st.error("Please select at least one stock.")
print(ticker)    
ticker = ticker[0].split(" - ")[0]
#ticker = st.text_input("Enter Stock Ticker")
shares = st.number_input("Number of Shares", min_value=1, step=1)
buy_price = st.number_input("Buy Price ($)", min_value=0.0, step=0.1)

if st.button("Add to Portfolio"):
    st.session_state.portfolio.append({
        "Ticker": ticker.upper(),
        "Shares": shares,
        "Buy Price": buy_price
    })
    st.success(f"Added {shares} shares of {ticker.upper()} at ${buy_price}")

if st.session_state.portfolio:
    df = pd.DataFrame(st.session_state.portfolio)
    st.subheader("📈 Your Portfolio")
    st.dataframe(df)
    
    # Optional: Calculate total investment
    total = sum(row["Shares"] * row["Buy Price"] for row in st.session_state.portfolio)
    st.markdown(f"### 💵 Total Investment: ${total:,.2f}")
