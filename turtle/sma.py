import backtrader as bt

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

    def stop(self):
        self.print_final_cash()

    def print_final_cash(self):
        print(f'Final cash: {self.broker.getvalue()}')

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.params.sma1)
        sma2 = bt.ind.SMA(period=self.params.sma2)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover > 0)
        self.signal_add(bt.SIGNAL_SHORT, crossover < 0)

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
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    cerebro.run()