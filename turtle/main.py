from datetime import datetime
from datetime import timedelta
import pandas as pd
import sma_detector as sdet
import sma


stocks = {
    "HS300": "data/hs300_stocks.csv",
    "ZZ500": "data/zz500_stocks.csv"
}


def main():
    print("Starting SMA Detector")
    end_date    = datetime.today()
    start_date  = end_date - timedelta(days=180)
    start_date  = start_date.strftime("%Y-%m-%d")
    end_date    = end_date.strftime("%Y-%m-%d")

    for stock_cls, stock_csv in stocks.items():
        print(f"Begin detect {stock_cls} golden crosses...")
        sdet.run(start_date, end_date, stock_csv, 1)
        print("Detect golden crosses done.")
        print("Do SMA Backtrade analysis...")

        df = pd.read_csv('data/golden_cross.csv', encoding='utf-8',parse_dates=['Last Cross Date'])
        for _, row in df.iterrows():
            code = row['Code']
            data = pd.read_csv(f'data/{code}.csv', parse_dates=['date'])
            profit = sma.runstrat(data)
            if profit > 0:
                print(f"sma 🎉 盈利: {code} {row['Name']}. profit is {profit:.2f}")
            # else:
                # print(f"sma 💔 亏损: {code} {row['Name']}. profit is {profit:.2f}")
            # print("----------------------------------")
        print("SMA Backtrade analysis done.")
        print(f"Finish {stock_cls}")
        print("....................................")
    print("Done. And good luck!")

if __name__ == "__main__":
    main()
