import pandas as pd
import matplotlib.pyplot as plt
import baostock_wrapper as bsw

def calculate_sma(df, window):
    return df['close'].rolling(window=window).mean()

def detect_golden_cross(df):
    df['SMA5'] = calculate_sma(df, 5)
    df['SMA20'] = calculate_sma(df, 20)
    df['Crossover'] = (df['SMA5'] > df['SMA20']) & (df['SMA5'].shift(1) <= df['SMA20'].shift(1))
    return df

def fetch_data(code):
    pass

def main(start_date, end_date):
    with open('data/hs300_stocks.csv', 'r') as fd:
        df = pd.read_csv(fd, parse_dates=['updateDate'])
    

    with bsw.BaoStockWrapper() as w:
        for _, row in df.iterrows():
            data = w.get_stock_data(code=row['code'], start_date=start_date, end_date=end_date)
            if data is None:
                break
            data = detect_golden_cross(data)
            if data['Crossover'].any():
                print(f"检测到 SMA5 上穿 SMA20 的信号！ 股票代码：{row['code']} {row['code_name']}")

if __name__ == "__main__":
    main(start_date='2025-01-01', end_date='2025-03-06')
