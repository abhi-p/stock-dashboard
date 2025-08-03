import streamlit as st

from data_handler.stock_data import *
from streamlit_javascript import st_javascript
from zoneinfo import ZoneInfo

import datetime

st.set_page_config(
    page_title="Stock Market Overiew",
    page_icon=":material/stacked_line_chart:",
    layout="wide", # How the page content should be laid out.
    initial_sidebar_state="auto"
)

# ----SESSION STATE -----

if 'timezone' not in st.session_state:
    timezone = st_javascript("""await (async () => {
                    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                    return userTimezone
                    })().then(returnValue => returnValue)""")
    if isinstance(timezone, int):
        st.stop()
    st.session_state['timezone'] = ZoneInfo(timezone)

data_handler = StockDataHandler()

page_state = {
    'current_time_price_page': datetime.datetime.now(st.session_state['timezone']).replace(microsecond=0, tzinfo=None),
    'tickers': "MSFT",
    'dark_mode': False,
    'toggle_theme': False,
    'financial_period': "Annual"
}

for key in page_state:
    if key not in st.session_state:
        st.session_state[key] = page_state[key]

for key in page_state:
    st.session_state[key] = st.session_state[key]



with st.sidebar:



    TICKERS = st.text_input(
        label="Securities:",
        value=st.session_state["tickers"],
        key='tickers'
    )

    st.write("eg.: MSFT, QQQ, SPY (max 5)")

    TICKERS = [item.strip() for item in TICKERS.split(",") if item.strip() != ""]

    #TICKERS = remove_duplicates(TICKERS)

    if len(TICKERS) > 5:
        st.error("Only first 5 tickers are shown")
        TICKERS = TICKERS[:10]

    _tickers = list()
    for TICKER in TICKERS:
        info = data_handler.fetch_info(TICKER)
        if isinstance(info, Exception):
            st.error(info)
            data_handler.fetch_info.clear(TICKER)
        else:
            QUOTE_TYPE = info.get('quoteType', "")
            if QUOTE_TYPE not in ["EQUITY", "ETF", "INDEX"]:
                st.error(f"{TICKER} has an invalid quoteType ({QUOTE_TYPE})")
            else:
                _tickers.append(TICKER)

    TICKERS = _tickers

    period_list = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

    PERIOD = st.selectbox(
        label="Period",
        options=period_list,
        index=3,
        placeholder="Select period...",
    )

    interval_list = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

    if PERIOD in interval_list:
        idx = interval_list.index(PERIOD)
        interval_list = interval_list[:idx]

    INTERVAL = st.selectbox(
        label="Interval",
        options=interval_list,
        index=len(interval_list) - 4,
        placeholder="Select interval...",
    )

    if len(TICKERS) == 1:

        TOGGLE_VOL = st.toggle(
            label="Volume",
            value=True
        )

        indicator_list = ['SMA_20', 'SMA_50', 'SMA_200', 'SMA_X', 'EMA_20', 'EMA_50', 'EMA_200', 'EMA_X', 'ATR', 'MACD', 'RSI']

        INDICATORS = st.multiselect(
            label="Technical indicators:",
            options=indicator_list
        )

        if 'SMA_X' in INDICATORS or 'EMA_X' in INDICATORS:
            TIME_SPAN = st.slider(
                label="Select time span:",
                min_value=10,  # The minimum permitted value.
                max_value=200,  # The maximum permitted value.
                value=30  # The value of the slider when it first renders.
            )
            INDICATORS = [indicator.replace("X", str(TIME_SPAN)) if '_X' in indicator else indicator for indicator in INDICATORS]

    st.write("")
    button = st.button("Refresh data")

    if button:
        st.session_state['current_time_price_page'] = datetime.datetime.now(st.session_state['timezone']).replace(microsecond=0, tzinfo=None)
        # fetch_table.clear()
        # fetch_info.clear()
        # fetch_history.clear()
        # #st.cache_data.clear()

    st.write("Last update:", st.session_state['current_time_price_page'])


   

st.title("Stock Market")

# #----FIRST SECTION----

col1, col2, col3 = st.columns(3, gap="small")

with col1:

    URL = "https://finance.yahoo.com/markets/world-indices/"

    df = data_handler.fetch_df(URL)

    INDICES = ["^GSPC", "^DJI", "^IXIC", "^N225", "^GDAXI", "^MERV"]

    st.subheader("Indices")
    if isinstance(df, Exception):
        st.error(df)
        data_handler.fetch_df.clear(URL)
    if isinstance(df, pd.DataFrame):
        with st.container(border=True):
            i = 0
            for _ in range(3):
                cols = st.columns(2, gap="small")
                for col in cols:
                    with col:
                        row = df[df['Symbol'] == INDICES[i]].iloc[0]
                        name = row['Name']
                        symbol = row['Symbol']
                        price, change, change_pt = row['Price'].split()
                        st.metric(
                            label=f'{name} ({symbol})',
                            value=f'{price}',
                            delta=f'{change} {change_pt}'
                        )
                    i += 1

with col2:

    URL = "https://finance.yahoo.com/markets/stocks/gainers/"

    df = data_handler.fetch_df(URL)

    st.subheader("Top Gainers")


    with st.container(border=True):
        i = 0
        for _ in range(3):
            cols = st.columns(2, gap="small")
            for col in cols:
                with col:
                    row = df.iloc[i]
                    name = row['Name']
                    symbol = row['Symbol']
                    price, change, change_pt = row['Price'].split()
                    st.metric(
                        label=f'{name} ({symbol})',
                        value=f'{price}',
                        delta=f'{change} {change_pt}'
                    )
                i += 1

with col3:

    URL = "https://finance.yahoo.com/markets/stocks/losers/"

    df = data_handler.fetch_df(URL)

    st.subheader("Top Losers")

    with st.container(border=True):
        i = 0
        for _ in range(3):
            cols = st.columns(2, gap="small")
            for col in cols:
                with col:
                    row = df.iloc[i]
                    name = row['Name']
                    symbol = row['Symbol']
                    price, change, change_pt = row['Price'].split()
                    st.metric(
                        label=f'{name} ({symbol})',
                        value=f'{price}',
                        delta=f'{change} {change_pt}'
                    )
                i += 1


