import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import csv
import requests
from streamlit.runtime.scriptrunner import RerunException

def legacy_rerun():
    raise RerunException(None)

st.set_page_config(page_title="MarketPULSE - US Stocks", layout="wide")

# --------- LOGIN FLOW ---------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def login_user(username, password):
    # Replace with your backend login API if needed
    # Currently accepts any non-empty user/pass for demo
    return username != "" and password != ""

def signup_user(username, password):
    # Replace with your backend signup API if needed
    return username != "" and password != ""

mode = st.sidebar.radio("Select Mode", ["Login", "Sign Up"])

if not st.session_state.logged_in:
    if mode == "Sign Up":
        st.title("Create Account")
        new_username = st.text_input("Username", key="signup_user")
        new_password = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            if new_username and new_password:
                if signup_user(new_username, new_password):
                    st.success("User created! Switch to Login to sign in.")
                else:
                    st.error("Sign up failed.")
            else:
                st.warning("Please fill both username and password.")
        st.stop()
    else:
        st.title("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if username and password:
                if login_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    legacy_rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.warning("Enter username and password.")
        st.stop()

st.sidebar.success(f"Welcome, {st.session_state['username']}")

# --------- STOCK SYMBOL LOAD ---------
@st.cache_data
def load_us_symbols():
    symbols = []
    try:
        with open("data/us_stocks.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol = row.get("Symbol", "").strip()
                if symbol:
                    symbols.append(symbol)
    except Exception as e:
        st.warning(f"Unable to read symbols: {e}")
    return symbols

symbols = load_us_symbols()

# --------- SEARCH & SELECT STOCK ---------
search_text = st.text_input("Search Stock Symbol", "").upper()
filtered_symbols = [s for s in symbols if search_text in s]

symbol = st.selectbox("Select Stock", filtered_symbols if filtered_symbols else symbols)

# --------- USD to INR conversion ---------
def usd_to_inr(usd_price):
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        rate = response.json().get("rates", {}).get("INR", None)
        if rate:
            return round(usd_price * rate, 2)
        else:
            return None
    except:
        return None

# --------- ANALYZE STOCK ---------
if st.button("Analyze"):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="90d")
    if hist.empty:
        st.error("No historical data found")
        st.stop()
    hist.reset_index(inplace=True)
    hist['Date'] = pd.to_datetime(hist['Date'])

    # Convert last close price USD->INR
    ltp_usd = hist.iloc[-1]['Close']
    ltp_inr = usd_to_inr(ltp_usd)
    ltp_display = f"₹{ltp_inr}" if ltp_inr else f"${ltp_usd}"

    st.header(f"{symbol} Stock Overview")
    st.metric(label="Last Price (INR)", value=ltp_display)

    # Candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=hist['Date'],
        open=hist['Open'],
        high=hist['High'],
        low=hist['Low'],
        close=hist['Close']
    )])
    st.plotly_chart(fig, use_container_width=True)

    # SMA Technical indicators
    hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
    hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=hist['Date'], y=hist['Close'], mode='lines', name=f'{symbol} Close'))
    fig2.add_trace(go.Scatter(x=hist['Date'], y=hist['SMA_20'], mode='lines', name='SMA 20'))
    fig2.add_trace(go.Scatter(x=hist['Date'], y=hist['SMA_50'], mode='lines', name='SMA 50'))
    fig2.update_layout(title="Technical Indicators", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig2, use_container_width=True)

    # Show basic news from yfinance
    try:
        news = ticker.news
        st.subheader("Latest News")
        for article in news[:5]:
            st.markdown(f"**{article.get('title','No Title')}**")
            st.markdown(f"{article.get('publisher','')} - {article.get('providerPublishTime','')}")
            url = article.get('link')
            if url:
                st.markdown(f"[Read more]({url})")
            st.markdown("---")
    except Exception:
        st.info("News not available")
