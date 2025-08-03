from data_handler.stock_data import *
from visualizer.plots import StockVisualizer
from streamlit_javascript import st_javascript
from zoneinfo import ZoneInfo
import datetime



# ----TIME ZONE----
if 'timezone' not in st.session_state:
    timezone = st_javascript("""await (async () => {
                    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                    return userTimezone
                    })().then(returnValue => returnValue)""")
    if isinstance(timezone, int):
        st.stop()
    st.session_state['timezone'] = ZoneInfo(timezone)

# ----SESSION STATE -----
all_my_widget_keys_to_keep = {
    'current_time_financials_page': datetime.datetime.now(st.session_state['timezone']).replace(microsecond=0, tzinfo=None),
    'tickers': "MSFT",
    'dark_mode': False,
    'toggle_theme': False,
    'financial_period': "Annual"
}

for key in all_my_widget_keys_to_keep:
    if key not in st.session_state:
        st.session_state[key] = all_my_widget_keys_to_keep[key]

for key in all_my_widget_keys_to_keep:
    st.session_state[key] = st.session_state[key]


# ---- INIT ----
data_handler = StockDataHandler()
visualizer = StockVisualizer()


# ---- SIDEBAR ----
with st.sidebar:

    TICKERS = st.text_input(
        label="Securities:",
        key='tickers'
    )

    TICKERS = [item.strip() for item in TICKERS.split(",") if item.strip() != ""]

    #TICKERS = data_handler.remove_duplicates(TICKERS)

    if len(TICKERS) > 10:
        st.error("Only first 10 tickers are shown")
        TICKERS = TICKERS[:10]

    _tickers = list()
    for TICKER in TICKERS:
        info = data_handler.fetch_info(TICKER)
        if isinstance(info, Exception):
            st.error(info)
            data_handler.fetch_info.clear(TICKER)
        else:
            QUOTE_TYPE = info.get('quoteType', "")
            if QUOTE_TYPE not in ["EQUITY"]:
                st.error(f"{TICKER} has an invalid quoteType ({QUOTE_TYPE})")
            else:
                _tickers.append(TICKER)

    TICKERS = _tickers

    TIME_PERIOD = st.radio(
        label="Time Period:",
        options=["Annual", "Quarterly"],
        key="financial_period"
    )

    st.write("")
    button = st.button("Refresh data")

    if button:
        st.session_state['current_time_financials_page'] = datetime.datetime.now(st.session_state['timezone']).replace(microsecond=0, tzinfo=None)
        data_handler.fetch_info.clear()
        data_handler.fetch_balance.clear()
        data_handler.fetch_income.clear()
        data_handler.fetch_cash.clear()
        st.cache_data.clear()

    st.write("Last update:", st.session_state['current_time_financials_page'])



# ---- MAINPAGE ----

st.title("Financials")

if len(TICKERS) == 0:
    st.header(f"Security: None")
    st.error("Error found")
    st.stop()

if len(TICKERS) == 1:

    TICKER = TICKERS[0]

    info = data_handler.fetch_info(TICKER)

    NAME = info.get('shortName', "")
    st.write(f'{NAME}')

    bs = data_handler.fetch_balance(TICKER, tp=TIME_PERIOD) #balance sheet
    ist = data_handler.fetch_income(TICKER, tp=TIME_PERIOD) #income statement
    cf = data_handler.fetch_cash(TICKER, tp=TIME_PERIOD) #cash flow

    CURRENCY = info.get('financialCurrency', "???")

    #----CAPITAL STRUCTURE-----

    st.header("Capital Structure")

    if isinstance(bs, Exception):
        st.error(bs)
        data_handler.fetch_balance.clear(TICKER, tp=TIME_PERIOD)
        st.stop()

    fig = visualizer.plot_capital(bs, ticker=TICKER, currency=CURRENCY)

    st.plotly_chart(
        fig,
        use_container_width=True,
        # theme=None
    )

    # ----BALANCE SHEET----

    st.header("Balance Sheet")

    st.write("The balance sheet refers to a financial statement that reports "
             "a company's assets, liabilities, and shareholder equity at a specific point in time.")


    fig = visualizer.plot_balance(bs[bs.columns[::-1]], ticker=TICKER, currency=CURRENCY)

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show components"):

        tab1, tab2, tab3 = st.tabs(["Assets", "Liabilities", "Equity"])

        with tab1:
            fig = visualizer.plot_assets(bs, ticker=TICKER, currency=CURRENCY)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig = visualizer.plot_liabilities(bs, ticker=TICKER, currency=CURRENCY)
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            fig = visualizer.plot_equity(bs, ticker=TICKER, currency=CURRENCY)
            st.plotly_chart(fig, use_container_width=True)



    with st.expander("Show data"):
        st.dataframe(
            data=bs,
            hide_index=False
        )


    # ----INCOME STATEMENT----

    st.header("Income Statement")

    st.write("The income statement refers to a financial statement that tracks the "
             "company's revenue, expenses, gains, and losses during a set period.")

    if isinstance(ist, Exception):
        st.error(ist)
        data_handler.fetch_income.clear(TICKER, tp=TIME_PERIOD)
        st.stop()

    fig = visualizer.plot_income(ist, ticker=TICKER, currency=CURRENCY)

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ratios"):
        tab1, tab2, tab3 = st.tabs(
            ["Net Margin", "Earnings per Share", "Price-to-Earnings Ratio"]
        )

        with tab1:

            st.write("Net profit margin measures how much net income or profit a company generates"
                     " as a percentage of its revenue.")

            try:
                fig = visualizer.plot_margins(ist, ticker=TICKER)
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    #theme=None
                )
            except:
                st.error("The data available is not enough to plot this ratio")

        with tab2:

            st.write("Basic earnings per share (EPS) is a rough measurement of the amount of a "
                     "company's profit that can be allocated to one share of its common stock.")

            try:
                fig = visualizer.plot_eps(TICKER)
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    #theme=None
                )
            except:
                st.error("The data available is not enough to plot this ratio")

        with tab3:

            st.write("The price-to-earnings (P/E) ratio measures a company's share price"
                     " relative to its earnings per share (EPS)")

            try:
                fig = visualizer.plot_pe_ratio(TICKER)
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    # theme=None
                )
            except:
                st.error("The data available is not enough to plot this ratio")

    with st.expander("Show data"):
        st.dataframe(
            data=ist,
            hide_index=False
        )

    # ----CASH FLOW----

    st.header("Cash Flow")

    st.write("The cash flow statement provides aggregate data regarding all cash inflows and"
             " all cash outflows during a given period")

    if isinstance(cf, Exception):
        st.error(cf)
        data_handler.fetch_cash.clear(TICKER, tp=TIME_PERIOD)
        st.stop()

    fig = visualizer.plot_cash(cf, ticker=TICKER, currency=CURRENCY)

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show data"):
        st.dataframe(
            data=cf,
            hide_index=False
        )

else:

    # ----CAPITAL STRUCTURE-----

    st.header("Capital Structure")

    fig = visualizer.plot_capital_multiple(TICKERS, tp=TIME_PERIOD)

    st.plotly_chart(
        fig,
        use_container_width=True,
        # theme=None
    )


    # ----BALANCE SHEET----

    st.header("Balance Sheet")

    fig = visualizer.plot_balance_multiple(TICKERS, tp=TIME_PERIOD)

    st.plotly_chart(fig, use_container_width=True)

    # ----INCOME STATEMENT----

    st.header("Income Statement")

    fig = visualizer.plot_income_multiple(TICKERS, tp=TIME_PERIOD)

    st.plotly_chart(fig, use_container_width=True)

    # ----CASH FLOW----

    st.header("Cash Flow")

    fig = visualizer.plot_cash_multiple(TICKERS, tp=TIME_PERIOD)

    st.plotly_chart(fig, use_container_width=True)
