import streamlit as st

# --- PAGE SETUP ---

stock_overview = st.Page(
    "pages/stock_overview.py",
    title="Stock Market",
    icon=":material/stacked_line_chart:", # from Material Design by Google
    default=True,
)

comp_financials = st.Page(
    "pages/stock_financials.py",
    title="Financials",
    icon=":material/finance:", # from https://fonts.google.com/icons
)

portfolio = st.Page(
    "pages/portfolio.py",
    title="portfolio",
    icon=":material/currency_exchange:",
)

commodity = st.Page(
    "pages/comodities.py",
    title="Commodity Market",
    icon=":material/oil_barrel:",
)

pg = st.navigation(pages=[stock_overview, comp_financials, portfolio, commodity])

# --- SHARED ON ALL PAGES ---
#st.logo("imgs/logo_friendly.png", size="large")

# --- RUN NAVIGATION ---
pg.run()