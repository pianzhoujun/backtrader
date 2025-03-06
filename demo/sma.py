# 选定一些股票，然后遍历从baostock拉取数据，分别计算5日和20日sma, 推测是否有上穿现象。 
# 这是第1步骤， 下一步是根据历史sma5 sma20算个回归模型，推测未来是否有上穿现象，需要重点关注的。


import pdb

import backtrader as bt
import baostock as bs
from datetime import datetime
import pandas as pd

code_list = [
    ("sh.601398", "工商银行"),
    ("sh.601988", "中国银行"),
    ("sh.601318", "中国平安"),
]


class BaoStockWrapper:
    def __enter__(self):
        lg = bs.login()
        print("bs login status: ", lg.error_code, lg.error_msg)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        bs.logout()


    def get_stock_data(self, code, start_date, end_date):
        rs = bs.query_history_k_data_plus(code,
            "date,code,open,high,low,close,volume,amount,adjustflag",
            start_date=start_date, 
            end_date=end_date,
            frequency="d", 
            adjustflag="3")

        if rs.error_code != "0":
            print("error code: ", rs.error_code)
            raise Exception(rs.error_msg)

        # 获取具体的信息
        result_list = []
        while (rs.error_code == '0') & rs.next():
            # 分页查询，将每页信息合并在一起
            result_list.append(rs.get_row_data())
        result = pd.DataFrame(result_list, columns=rs.fields)

        result['date'] = pd.to_datetime(result['date'])
        result['open'] = pd.to_numeric(result['open'])
        result['high'] = pd.to_numeric(result['high'])
        result['low'] = pd.to_numeric(result['low'])
        result['close'] = pd.to_numeric(result['close'])
        result['volume'] = pd.to_numeric(result['volume'])
        result['amount'] = pd.to_numeric(result['amount'])

        return result

class SmaCross(bt.SignalStrategy):
    params = dict(sma1=5, sma2=20)

    def notify_order(self, order):
        if not order.alive():
            print('{} {} {}@{}'.format(
                bt.num2date(order.executed.dt),
                'buy' if order.isbuy() else 'sell',
                order.executed.size,
                order.executed.price)
            )

    def notify_trade(self, trade):
        if trade.isclosed:
            print('profit {}'.format(trade.pnlcomm))

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.params.sma1)
        sma2 = bt.ind.SMA(period=self.params.sma2)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)

def runstrat(data):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000.0)
    data0 = bt.feeds.PandasData(dataname=data,
        datetime='date',
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
    )
    cerebro.adddata(data0)
    cerebro.addstrategy(SmaCross)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.run()
    cerebro.plot()

def main():
    today = datetime.today().strftime("%Y-%m-%d")
    start_date = "2025-01-01"

    with BaoStockWrapper() as bsw:
        for code, name in code_list:
            print("开始处理：{}".format(name))
            df = bsw.get_stock_data(code, start_date, today)
            runstrat(df)

if __name__ == '__main__':
    main()