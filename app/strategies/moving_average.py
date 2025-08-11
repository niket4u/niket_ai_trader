
import pandas as pd

def moving_average_crossover(df: pd.DataFrame, fast: int=5, slow: int=20):
    sfast = df['close'].rolling(fast).mean()
    sslow = df['close'].rolling(slow).mean()
    signal = (sfast > sslow).astype(int).diff().fillna(0)
    return signal.iloc[-1]  # +1 buy, -1 sell, 0 none
