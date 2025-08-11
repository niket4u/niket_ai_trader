
import pandas as pd
import yfinance as yf
from tenacity import retry, wait_fixed, stop_after_attempt

@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def get_history(ticker: str, period: str="6mo", interval: str="1d") -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise RuntimeError(f"No data for {ticker}")
    df = df.reset_index().rename(columns=str.lower)
    return df

def get_latest_price(ticker: str) -> float:
    df = get_history(ticker, period="5d", interval="1m")
    return float(df.tail(1)["close"].values[0])
