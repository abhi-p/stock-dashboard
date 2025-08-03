import streamlit as st
import pandas as pd
from data_handler.stock_data import StockDataHandler

st.set_page_config(page_title="Portfolio Tracker", layout="wide")

# CSS styling for a cleaner look
st.markdown("""
    <style>
    .stock-card {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .gain {
        color: green;
        font-weight: bold;
    }
    .loss {
        color: red;
        font-weight: bold;
    }
    .ticker-title {
        font-size: 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize portfolio
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

data_handler = StockDataHandler()
us_tickers = data_handler.get_us_tickers()

st.title("💼 Your Portfolio")

# Ticker selection
with st.expander("➕ Add Stock to Portfolio"):
    ticker = st.multiselect("Select a ticker:", us_tickers["search_string"].tolist(), max_selections=1, default=["AAPL - Apple Inc.             - XNAS"])
    if ticker:
        ticker = ticker[0].split(" - ")[0]
        shares = st.number_input("Number of Shares", min_value=1, step=1, key="shares_input")
        buy_price = st.number_input("Buy Price ($)", min_value=0.0, step=0.1, key="price_input")
        if st.button("Add to Portfolio"):
            found=False
            for i,stocks in enumerate(st.session_state.portfolio):
                if stocks['Ticker']==ticker.upper():
                    st.session_state.portfolio[i]['Buy Price']=  (st.session_state.portfolio[i]['Buy Price']*st.session_state.portfolio[i]['Shares']+buy_price*shares)/(shares+st.session_state.portfolio[i]['Shares'])
                    st.session_state.portfolio[i]['Shares']+=shares
                    found=True
                    break
            if not found:
                st.session_state.portfolio.append({
                    "Ticker": ticker.upper(),
                    "Shares": shares,
                    "Buy Price": buy_price
                })
            st.success(f"✅ Added {shares} shares of {ticker.upper()} at ${buy_price}")
            print(st.session_state.portfolio)


# Display portfolio
if st.session_state.portfolio:
    total_value = 0.0
    st.markdown("### 📈 Current Holdings")

    for i, stock in enumerate(st.session_state.portfolio):
        info = data_handler.get_price_info(stock["Ticker"])
        current_price = info.get("current_price", 0.0)
        prev_close = info.get("previous_close", 0.0)

        shares = stock["Shares"]
        buy_price = stock["Buy Price"]
        total_stock_value = current_price * shares
        change_from_buy = current_price - buy_price
        change_today = current_price - prev_close

        gain_loss_class = "gain" if change_from_buy >= 0 else "loss"
        change_today_class = "gain" if change_today >= 0 else "loss"

        total_value += total_stock_value

        # Create a styled "card"
        with st.container():
            st.markdown(f"""
                <div class="stock-card">
                    <div class="ticker-title">{stock['Ticker']}</div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                        <div><strong>Shares:</strong> {shares}</div>
                        <div><strong>Average Price: </strong> ${buy_price:.2f}</div>
                        <div><strong>Current:</strong> ${current_price:.2f}</div>
                        <div><strong>Total:</strong> ${total_stock_value:.2f}</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                        <div><strong>Change from Buy:</strong> <span class="{gain_loss_class}">${change_from_buy:.2f}</span></div>
                        <div><strong>Today's Change:</strong> <span class="{change_today_class}">${change_today:.2f}</span></div>
                        <form style="margin: 0;" action="" method="post">
                            <button type="submit" name="delete_{i}" style="color: red; background: none; border: none; font-weight: bold;">🗑 Delete</button>
                        </form>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Delete logic
        # Native Streamlit delete button
            if st.button("🗑 Delete", key=f"delete_{i}"):
                print(st.session_state.portfolio)
                del st.session_state.portfolio[i]
                st.rerun()

            st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown(f"### 💵 **Total Portfolio Value**: ${total_value:,.2f}")
else:
    st.info("Your portfolio is currently empty. Add a stock to get started.")
