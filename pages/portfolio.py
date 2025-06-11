import streamlit as st
import pandas as pd

# You can use session state to keep track of portfolio across interactions
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

st.title("📊 Portfolio Tracker")

ticker = st.text_input("Enter Stock Ticker")
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
