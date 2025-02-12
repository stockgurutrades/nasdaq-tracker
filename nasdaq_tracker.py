import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import time

# Define NASDAQ tickers (Example: Add more stocks as needed)
nasdaq_tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA", "META", "AMD", "NFLX", "INTC","ADBE", "PYPL", "CSCO", "PEP", "AVGO", "TXN", "COST", "QCOM", "HON", "SBUX",
                  "AMGN", "INTU", "ISRG", "BKNG", "MDLZ", "AMAT", "ADI", "LRCX", "MU", "GILD","ADP", "VRTX", "FISV", "ATVI", "CSX", "MRVL", "KLAC", "MCHP", "ORLY", "NXPI",
    "KDP", "PANW", "EXC", "MNST", "CTAS", "XEL", "IDXX", "ASML", "TEAM", "WDAY","SNPS", "CDNS", "ANSS", "CTSH", "FAST", "VRSK", "EBAY", "ROST", "PAYX", "PCAR",
    "SIRI", "WBA", "BIDU", "BIIB", "LULU", "MAR", "MTCH", "CHTR", "SWKS", "ILMN","ALGN", "DOCU", "SGEN", "OKTA", "ZS", "CRWD", "DDOG", "ZM", "PDD", "JD",
    "BMRN", "MELI", "CPRT", "DLTR", "SPLK", "VRSN", "NTES", "KLAC", "NXPI", "ODFL","ON", "PCAR", "PAYX", "PYPL", "QCOM", "REGN", "ROST", "SBUX", "SGEN", "SIRI",
    "SNPS", "SPLK", "SWKS", "TEAM", "TMUS", "TSLA", "TXN", "VRSK", "VRSN", "VRTX","WBA", "WDAY", "XEL", "ZM", "ZS"]


def get_stock_data(tickers):
    stock_list = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")  # Fetch last 5 days of history
            if hist.empty:
                print(f"No data for {ticker}, skipping.")
                continue

            latest_price = hist["Close"].iloc[-1]
            prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else latest_price
            daily_change = ((latest_price - prev_close) / prev_close) * 100 if prev_close else 0
            direction = "Green" if daily_change > 0 else "Red"
            market_cap = stock.info.get("marketCap", 0)  # Default to 0 if missing

            stock_list.append({"Ticker": ticker, "Market Cap": market_cap,
                               "Price": latest_price, "Daily Change (%)": daily_change, "Direction": direction})
            time.sleep(0.5)  # Delay to prevent rate-limiting
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            continue

    return pd.DataFrame(stock_list)

# Streamlit UI
st.title("NASDAQ Stock Tracker")

# Auto-refresh logic
refresh_time = 30  # Refresh every 30 seconds
if "last_refresh" not in st.session_state or time.time() - st.session_state.last_refresh > refresh_time:
    st.session_state.last_refresh = time.time()
    st.rerun()

# Fetch stock data
nasdaq_data = get_stock_data(nasdaq_tickers)

# Check if data is empty before proceeding
if nasdaq_data.empty:
    st.error("No stock data available. Please try again later. Yahoo Finance may be restricting data access.")
else:
    # Ensure "Direction" column exists before using it
    if "Direction" in nasdaq_data.columns:
        # Split into Green and Red stocks
        green_stocks = nasdaq_data[nasdaq_data["Direction"] == "Green"]
        red_stocks = nasdaq_data[nasdaq_data["Direction"] == "Red"]

        # Pie Chart Visualization (Enhanced Look)
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie([len(green_stocks), len(red_stocks)], labels=["Green", "Red"], autopct="%1.1f%%", colors=["limegreen", "red"],
               startangle=90, wedgeprops={"edgecolor": "black", "linewidth": 1.5})
        ax.set_title("NASDAQ: Green vs Red Stocks", fontsize=14, fontweight='bold')
        st.pyplot(fig)

        # Display tables
        st.subheader("Green Stocks")
        st.dataframe(green_stocks.sort_values(by="Daily Change (%)", ascending=False))

        st.subheader("Red Stocks")
        st.dataframe(red_stocks.sort_values(by="Daily Change (%)", ascending=True))

        st.subheader("All Stocks")
        st.dataframe(nasdaq_data.sort_values(by="Market Cap", ascending=False))
    else:
        st.error("Data error: 'Direction' column is missing.")
