import os
import time
import pandas as pd
# import matplotlib.pyplot as plt
import baostock_wrapper as bsw

def calculate_sma(df, window):
    return df['close'].rolling(window=window).mean()

def detect_golden_cross(df):
    df['SMA5'] = calculate_sma(df, 5)
    df['SMA20'] = calculate_sma(df, 20)
    df['Crossover'] = (df['SMA5'] > df['SMA20']) & (df['SMA5'].shift(1) <= df['SMA20'].shift(1))
    return df

def run(start_date, end_date):
    with open('data/hs300_stocks.csv', 'r') as fd:
        df = pd.read_csv(fd, parse_dates=['updateDate'])
    
    gloden_cross = {
        "Code": [],
        "Name": [],
        "Last Cross Date": []
    }
    
    with bsw.BaoStockWrapper() as w:
        for _, row in df.iterrows():
            local_file = f'data/{row["code"]}.csv'
            if not os.path.exists(local_file) or os.stat(local_file).st_mtime < time.time()-43200:
                data = w.get_stock_data(code=row['code'], start_date=start_date, end_date=end_date)
                if data is None:
                    break
                data.to_csv(f'data/{row["code"]}.csv', index=False)
            else:
                data = pd.read_csv(f'data/{row["code"]}.csv', parse_dates=['date'])
            data = detect_golden_cross(data)
            if not data['Crossover'].any():
                continue
            last_cross = data['Crossover'].idxmax()
            if last_cross >= len(data)-7:
                gloden_cross["Code"].append(row["code"])
                gloden_cross['Name'].append(row['code_name'])
                gloden_cross['Last Cross Date'].append(data.iloc[last_cross]['date'])
    for _, row in pd.DataFrame(gloden_cross).iterrows():
        print(f'{row["Name"]} - {row["Code"]}: {row["Last Cross Date"]}')
    with open('data/golden_cross.csv', 'w') as fd:
        pd.DataFrame(gloden_cross).to_csv(fd, index=False)


if __name__ == "__main__":
   run(start_date='2025-01-01', end_date='2025-03-10')
