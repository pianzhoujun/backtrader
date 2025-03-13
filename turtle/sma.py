import backtrader as bt

debug = False

def log(message):
    if debug:
        print(message)

class SmaCross(bt.SignalStrategy):
    params = dict(sma1=5, sma2=10, hold_days=20)  # 添加持有天数参数

    def __init__(self):
        self.sma1 = bt.ind.SMA(period=self.params.sma1)
        self.sma2 = bt.ind.SMA(period=self.params.sma2)
        self.crossover = bt.ind.CrossOver(self.sma1, self.sma2)  # 计算均线交叉
        self.bar_executed = {}  # 记录买入的时间点

        self.signal_add(bt.SIGNAL_LONG, self.crossover)  # 5日均线上穿10日均线买入
        self.signal_add(bt.SIGNAL_SHORT, self.crossover)  # 5日均线下穿10日均线卖出

    def next(self):
        """ 在每根K线执行交易检查 """
        date = self.datas[0].datetime.date(0)
        position = self.getposition()

        if self.crossover > 0:  # 触发买入信号
            log(f"📈 SMA5 上穿 SMA10，触发买入信号")
            self.buy()
            self.bar_executed[date] = date 

        elif self.crossover < 0 and position.size > 0:  # 触发卖出信号
            log(f"📉 SMA5 下穿 SMA10，触发卖出信号")
            self.sell()

        # 20 天后自动卖出
        for buy_date, _ in list(self.bar_executed.items()):
            if (date - buy_date).days >= self.params.hold_days and position.size > 0:
                log(f"📆 持有{self.params.hold_days}天，强制卖出 {date}")
                self.sell()
                del self.bar_executed[buy_date]  # 卖出后删除记录

    def notify_order(self, order):
        """ 监听订单状态变化 """
        if not order.alive():
            log(f"{bt.num2date(order.executed.dt)} - {'买入' if order.isbuy() else '卖出'} {order.executed.size} @ {order.executed.price}")

    def notify_trade(self, trade):
        """ 监听交易完成，输出盈亏 """
        if trade.isclosed:
            log(f"🎉 盈利: {trade.pnlcomm:.2f}" if trade.pnlcomm > 0 else f"💔 亏损: {trade.pnlcomm:.2f}")

    def stop(self):
        """ 回测结束，输出最终净值 """
        final_value = self.broker.getvalue()
        start_value = self.broker.startingcash
        net_profit = final_value - start_value

        log("=" * 30)
        log(f"📊 回测结束 - 期末资金: {final_value:.2f}")
        log(f"💰 期初资金: {start_value:.2f}")
        log(f"🚀 策略净利润: {net_profit:.2f}")
        log("=" * 30)


def runstrat(data, plot=False):
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
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    cerebro.run()

    profit = cerebro.broker.getvalue() - cerebro.broker.startingcash
    if plot:
        cerebro.plot()
    return profit

if __name__ == '__main__':
    import pandas as pd
    df = pd.read_csv("data/sh.601318.csv", parse_dates=['date'])
    debug = True
    runstrat(df, True)