import os
import time
import pandas as pd
# import matplotlib.pyplot as plt
import baostock_wrapper as bsw

def calculate_sma(df, window):
    return df['close'].rolling(window=window).mean()

def detect_golden_cross(df):
    df = df.copy()  # 避免修改原始 DataFrame
    df['SMA5'] = calculate_sma(df, 5)
    df['SMA10'] = calculate_sma(df, 10)

    prev_sma5 = df['SMA5'].shift(1)
    prev_sma10 = df['SMA10'].shift(1)

    df['Crossover'] = (df['SMA5'] > df['SMA10']) & (prev_sma5 <= prev_sma10)
    return df

def run(start_date, end_date, stock_file, detect_days=7):
    df = pd.read_csv(stock_file, parse_dates=['updateDate'], encoding='utf-8')
    
    golden_cross = {
        "Code": [],
        "Name": [],
        "Last Cross Date": []
    }
    
    with bsw.BaoStockWrapper() as w:
        for _, row in df.iterrows():
            local_file = f'data/{row["code"]}.csv'
            if not os.path.exists(local_file) or os.stat(local_file).st_mtime < time.time()-3600 * 12:
                data = w.get_stock_data(code=row['code'], start_date=start_date, end_date=end_date)
                if data is None:
                    break
                data.to_csv(f'data/{row["code"]}.csv', index=False)
            else:
                data = pd.read_csv(f'data/{row["code"]}.csv', parse_dates=['date'])
            cross_points = detect_golden_cross(data)
            cross_points = cross_points[cross_points['Crossover'] == True]
            if cross_points.empty:
                continue
            
            # 取最近一次金叉的日期
            last_cross_date = cross_points['date'].iloc[-1]

            # 如果最近的金叉在过去 detect_days 天内
            if last_cross_date >= data['date'].iloc[-detect_days]:
                golden_cross['Code'].append(row['code'])
                golden_cross['Name'].append(row['code_name'])
                golden_cross['Last Cross Date'].append(last_cross_date)
    # for _, row in pd.DataFrame(golden_cross).iterrows():
        # print(f'{row["Name"]} - {row["Code"]}: {row["Last Cross Date"]}')
    # with open('data/golden_cross.csv', 'w') as fd:
    pd.DataFrame(golden_cross).to_csv('data/golden_cross.csv', index=False)

def test_sma(code_list: list):
    # file = 'data/sh.601318.csv'
    # file = 'data/sh.600989.csv'

    for code in code_list:
        file = f'data/{code}.csv'
        if not os.path.exists(file) or os.stat(file).st_mtime < time.time()-3600 * 3:
            from datetime import datetime
            from datetime import timedelta
            today = datetime.today()
            end_date = today.strftime('%Y-%m-%d')
            start_date = today - timedelta(days=360)
            start_date = start_date.strftime('%Y-%m-%d')

            with bsw.BaoStockWrapper() as w:
                data = w.get_stock_data(code=code, start_date=start_date, end_date=end_date)
                if data is None:
                    break
                data.to_csv(f'data/{code}.csv', index=False)

        df = pd.read_csv(file, parse_dates=['date'], encoding='utf-8')
        sma5 = calculate_sma(df, 5)
        sma10 = calculate_sma(df,10)
        print(sma5)
        print(sma10)

        print("----------------------------------------")
        cross_points = detect_golden_cross(df)
        cross_points = cross_points[cross_points['Crossover'] == True]
        last_cross_date = cross_points['date'].iloc[-1]

        golden_cross = {
            "Code": [],
            "Last Cross Date": []
        }

        # 如果最近的金叉在过去 detect_days 天内
        if last_cross_date >= df['date'].iloc[-7]:
            golden_cross['Code'].append(code)
            golden_cross['Last Cross Date'].append(last_cross_date)
        print(pd.DataFrame(golden_cross))
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


if __name__ == "__main__":
#    run(start_date='2025-01-01', end_date='2025-03-10')
    test_sma(('sh.600183', ))
