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


# st.markdown("""
#     <style>
#     .stock-card {
#         background-color: #f9f9f9;
#         padding: 1rem;
#         border-radius: 12px;
#         margin-bottom: 1rem;
#         box-shadow: 0 2px 6px rgba(0,0,0,0.05);
#     }
#     .gain {
#         color: green;
#         font-weight: bold;
#     }
#     .loss {
#         color: red;
#         font-weight: bold;
#     }
#     </style>
# """, unsafe_allow_html=True)

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
sort_options = {
    "Ticker": lambda x: x["Ticker"],
    "Total Value": lambda x: data_handler.get_price_info(x["Ticker"]).get("current_price", 0.0) * x["Shares"],
    "Today's Change": lambda x: (
        data_handler.get_price_info(x["Ticker"]).get("current_price", 0.0)
        - data_handler.get_price_info(x["Ticker"]).get("previous_close", 0.0)
    ),
    "All-Time Return": lambda x: (
        data_handler.get_price_info(x["Ticker"]).get("current_price", 0.0)
        - x["Buy Price"]
    )
}

sort_by = st.selectbox("🔽 Sort portfolio by:", list(sort_options.keys()))
ascending = st.checkbox("⬆️ Ascending", value=False)

# Sort portfolio based on selected criteria
st.session_state.portfolio = sorted(
    st.session_state.portfolio,
    key=sort_options[sort_by],
    reverse=not ascending
)

if st.session_state.portfolio:
    total_value = 0.0
    st.markdown("### 📈 Current Holdings")

    st.markdown("""
    <div class="stock-card" style="background: transparent; box-shadow: none; font-weight: bold;">
        <div style="display: flex; justify-content: space-between; font-size: 16px; border-bottom: 1px solid #ddd; padding-bottom: 0.5rem;">
            <div style="width: 25%;">Ticker</div>
            <div style="width: 25%;">Total Value</div>
            <div style="width: 25%;">Today's Change</div>
            <div style="width: 25%;">All-Time Return</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    for i, stock in enumerate(st.session_state.portfolio):
        info = data_handler.get_price_info(stock["Ticker"])
        current_price = info.get("current_price", 0.0)
        prev_close = info.get("previous_close", 0.0)

        shares = stock["Shares"]
        buy_price = stock["Buy Price"]
        ticker = stock["Ticker"]

        total_value = current_price * shares
        total_cost = buy_price * shares

        change_today = current_price - prev_close
        change_today_pct = (change_today / prev_close) * 100 if prev_close else 0

        all_time_return = current_price - buy_price
        all_time_return_pct = (all_time_return / buy_price) * 100 if buy_price else 0

        return_color_class = "gain" if all_time_return_pct >= 0 else "loss"
        today_color_class = "gain" if change_today_pct >= 0 else "loss"

        with st.container():
            st.markdown(f"""
            <div class="stock-card">
                <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 18px;">
                    <div>{ticker}</div>
                    <div>${total_value:,.2f}</div>
                    <div class="{today_color_class}">${change_today:.2f} ({change_today_pct:.2f}%)</div>
                    <div class="{return_color_class}">${all_time_return:.2f} ({all_time_return_pct:.2f}%)</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; color: #555;">
                    <div>{shares} shares</div>
                    <div></div>
                    <div class="{today_color_class}">{change_today_pct:.2f}% today</div>
                    <div class="{return_color_class}">{all_time_return_pct:.2f}% all-time</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🗑 Remove", key=f"delete_{i}"):
                del st.session_state.portfolio[i]
                st.rerun()

    st.markdown(f"### 💵 **Total Portfolio Value**: ${total_value:,.2f}")
else:
    st.info("Your portfolio is currently empty. Add a stock to get started.")
