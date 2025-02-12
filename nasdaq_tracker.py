import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Define NASDAQ tickers (Example: Add more stocks as needed)
nasdaq_tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA", "META", "AMD", "NFLX", "INTC","ADBE", "PYPL", "CSCO", "PEP", "AVGO", "TXN", "COST", "QCOM", "HON", "SBUX",
                  "AMGN", "INTU", "ISRG", "BKNG", "MDLZ", "AMAT", "ADI", "LRCX", "MU", "GILD","ADP", "VRTX", "FISV", "ATVI", "CSX", "MRVL", "KLAC", "MCHP", "ORLY", "NXPI",
    "KDP", "PANW", "EXC", "MNST", "CTAS", "XEL", "IDXX", "ASML", "TEAM", "WDAY","SNPS", "CDNS", "ANSS", "CTSH", "FAST", "VRSK", "EBAY", "ROST", "PAYX", "PCAR",
    "SIRI", "WBA", "BIDU", "BIIB", "LULU", "MAR", "MTCH", "CHTR", "SWKS", "ILMN","ALGN", "DOCU", "SGEN", "OKTA", "ZS", "CRWD", "DDOG", "ZM", "PDD", "JD",
    "BMRN", "MELI", "CPRT", "DLTR", "SPLK", "VRSN", "NTES", "KLAC", "NXPI", "ODFL","ON", "PCAR", "PAYX", "PYPL", "QCOM", "REGN", "ROST", "SBUX", "SGEN", "SIRI",
    "SNPS", "SPLK", "SWKS", "TEAM", "TMUS", "TSLA", "TXN", "VRSK", "VRSN", "VRTX","WBA", "WDAY", "XEL", "ZM", "ZS"]


def get_stock_data(tickers):
    batch_size = 20  # Fetch stocks in batches to avoid request limits
    stock_list = []

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        try:
            data = yf.download(batch, period="5d", interval="1d")["Adj Close"].ffill()
            prev_close = data.shift(1).iloc[-1]  # Get previous close even if the market is closed
            if data.empty:
                print(f"No data returned for batch: {batch}")
                continue
        except Exception as e:
            print(f"Error fetching batch {batch}: {e}")
            continue

        for ticker in batch:
            try:
                stock = yf.Ticker(ticker)
                market_cap = stock.info.get("marketCap", 0)  # Default to 0 if missing
                if ticker in data.columns and ticker in prev_close.index and not pd.isna(data[ticker].iloc[-1]):
                    latest_price = data[ticker].iloc[-1]
                    daily_change = ((latest_price - prev_close[ticker]) / prev_close[ticker]) * 100
                    direction = "Green" if daily_change > 0 else "Red"
                    stock_list.append({"Ticker": ticker, "Market Cap": market_cap, 
                                       "Price": latest_price, "Daily Change (%)": daily_change, "Direction": direction})
                else:
                    print(f"Missing data for {ticker}")
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")

    return pd.DataFrame(stock_list)

# Streamlit UI
st.title("NASDAQ Stock Tracker")

# Fetch stock data
nasdaq_data = get_stock_data(nasdaq_tickers)

# Check if data is empty before proceeding
if nasdaq_data.empty:
    st.error("No stock data available. Please try again later. This could be due to Yahoo Finance restrictions.")
else:
    # Ensure "Direction" column exists before using it
    if "Direction" in nasdaq_data.columns:
        # Count Green vs Red stocks
        green_count = len(nasdaq_data[nasdaq_data["Direction"] == "Green"])
        red_count = len(nasdaq_data[nasdaq_data["Direction"] == "Red"])
        total_count = len(nasdaq_data)

        green_percentage = (green_count / total_count) * 100
        red_percentage = (red_count / total_count) * 100

        # Pie Chart Visualization
        fig, ax = plt.subplots()
        ax.pie([green_count, red_count], labels=["Green", "Red"], autopct="%1.1f%%", colors=["green", "red"])
        ax.set_title("NASDAQ: Green vs Red Stocks")
        st.pyplot(fig)

        # Sorting Options
        sort_option = st.selectbox("Sort stocks by:", ["Market Cap", "Daily Change (%)"], index=0)

        # Sorting Data
        if sort_option == "Market Cap":
            sorted_data = nasdaq_data.sort_values(by="Market Cap", ascending=False)
        else:
            sorted_data = nasdaq_data.sort_values(by="Daily Change (%)", ascending=False)

        # Display Data
        st.dataframe(sorted_data)
    else:
        st.error("Data error: 'Direction' column is missing.")
