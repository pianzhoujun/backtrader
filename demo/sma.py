# 选定一些股票，然后遍历从baostock拉取数据，分别计算5日和20日sma, 推测是否有上穿现象。 
# 这是第1步骤， 下一步是根据历史sma5 sma20算个回归模型，推测未来是否有上穿现象，需要重点关注的。

import backtrader as bt
import baostock as bs
from datetime import datetime
import pandas as pd

import baostock_wrapper as bsw

code_list = [
    ("sh.601398", "工商银行"),
    ("sh.601988", "中国银行"),
    ("sh.601318", "中国平安"),
]

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
            if trade.iswon():
                print(f'won profit {trade.pnlcomm}')
            else:
                print(f'lost loss {trade.pnlcomm}')

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
    # cerebro.plot()

def main():
    today = datetime.today().strftime("%Y-%m-%d")
    start_date = "2025-01-01"

    with bsw.BaoStockWrapper() as bs:
        for code, name in code_list:
            print("开始处理：{}".format(name))
            df = bs.get_stock_data(code, start_date, today)
            runstrat(df)

if __name__ == '__main__':
    main()