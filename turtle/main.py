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
    end_date = datetime.today()
    start_date = end_date - timedelta(days=180)
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    for stock_cls, stock_csv in stocks.items():
        print(f"Begin detect {stock_cls} and regress")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        sdet.run(start_date, end_date, stock_csv, 7)
        print("Detect golden crosses done.")
        print("-----------------------------------")
        print("\nDo SMA Backtrade analysis...")
    
        df = pd.read_csv('data/golden_cross.csv', parse_dates=['Last Cross Date'])
        for _, row in df.iterrows():
            code = row['Code']
            print(f"sma analysis of {code} {row['Name']}")
            data = pd.read_csv(f'data/{code}.csv', parse_dates=['date'])
            sma.runstrat(data)
            print("----------------------------------")
        print("SMA Backtrade analysis done.")
        print(f"Finish {stock_cls}")
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print("Done. And good luck!")

if __name__ == "__main__":
    main()
