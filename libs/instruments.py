import pandas as pd
import datetime
from libs.pubsub import get_ps_1


def get_instruments():
    'TODO: check if this can be populated based on subscriptions'
    'call all these index symbol'
    symbols = [['BIOCON', 2911489, 'BIOCON.NS', 'EQUITY'],
               ['AXISBANK', 1510401, 'AXISBANK.NS', 'EQUITY'],
               ['SUNPHARMA', 857857, 'SUNPHARMA.NS', 'EQUITY'],
               ['ADANIPORTS', 3861249, 'ADANIPORTS.NS', 'EQUITY'],
               ['HINDALCO', 348929, 'HINDALCO.NS', 'EQUITY'],
               ['TATAPOWER', 877057, 'TATAPOWER.NS', 'EQUITY'],
               ['NIFTY 50', 256265, '^NSEI', 'INDEX'],
               ]
    instruments = [{'symbol': x[0], 'token': x[1], 'ysymbol': x[2], 'type': x[3]}
                   for x in symbols]
    return instruments


def get_instrument_tokens():
    return [x['token'] for x in get_instruments()]


class OHLC:
    def __init__(self, symbol, tf_min) -> None:
        self.symbol = symbol
        self.tf_min = tf_min
        self.tf = datetime.timedelta(minutes=tf_min)
        self.df_ohlc = pd.DataFrame()
        self.s_buffer = pd.Series()
        self.ohlc_cbs = set()
        self.r = get_ps_1()

    def subscribe_ohlc(self, cb):
        self.ohlc_cbs.add(cb)

    def feed_price(self, timestamp, price):
        ''
        if(self.s_buffer.empty):
            self.s_buffer['Open'] = self.s_buffer['High'] = self.s_buffer['Low'] = price
            # if(self.df_ohlc.empty):
            #     'This should not happen because of init_history'
            #     'timestamp should be a multiple of tf'
            #     self.s_buffer.name = timestamp - \
            #         datetime.timedelta(minutes=timestamp.minute % self.tf)
            # else:
            #     self.s_buffer.name = self.df_ohlc.index[-1] + self.tf
            self.s_buffer.name = timestamp - \
                                datetime.timedelta(minutes=timestamp.minute % self.tf_min, seconds=timestamp.second)
        else:
            self.s_buffer['High'] = max(
                self.s_buffer['High'], price)
            self.s_buffer['Low'] = min(
                self.s_buffer['Low'], price)
            if(timestamp >= (self.s_buffer.name + self.tf)):
                self.s_buffer['Close'] = price
                # import pdb; pdb.set_trace()
                # print(self.symbol, self.tf_min, len(self.df_ohlc))
                self.df_ohlc = self.df_ohlc.append(self.s_buffer)
                # print(self.symbol, self.tf_min, len(self.df_ohlc))
                for cb in self.ohlc_cbs:
                    cb()
                self.s_buffer = pd.Series()


class Instrument:
    def __init__(self, symbol, token, ltf_min=3, htf_min=15) -> None:
        self.r = get_ps_1()
        self.symbol = symbol
        self.token = token
        self.ltf_min = ltf_min
        self.htf_min = htf_min
        self.ohlc_ltf = OHLC(symbol, ltf_min)
        self.ohlc_htf = OHLC(symbol, htf_min)
        self.last_price = None
        self.last_timestamp = None  # TODO remove
        self.ohlcs = {ltf_min: self.ohlc_ltf, htf_min: self.ohlc_htf}
        self.ohlc_ltf.subscribe_ohlc(self.ltf_update)
        self.ohlc_htf.subscribe_ohlc(self.htf_update)
        self.cbs = set()

    def ltf_update(self):
        self.r.publish(f'INSTRUMENT-{self.symbol}-OHLC-{self.ltf_min}', {'tftype': 'LTF', 'symbol': self.symbol, 'token': self.token,
                                                              'timestamp': self.last_timestamp, 'last_price': self.last_price, 'ohlcs': self.ohlc_ltf.df_ohlc, })

    def htf_update(self):
        self.r.publish(f'INSTRUMENT-{self.symbol}-OHLC-{self.htf_min}', {'tftype': 'HTF', 'symbol': self.symbol, 'token': self.token,
                                                              'timestamp': self.last_timestamp, 'last_price': self.last_price, 'ohlcs': self.ohlc_htf.df_ohlc, })

    def set_ohlcs(self, tfmin, df_ohlcs):
        self.ohlcs[tfmin].df_ohlc = df_ohlcs
        if(tfmin == self.ltf_min):
            self.ltf_update()
        if(tfmin == self.htf_min):
            self.htf_update()

    def feed_tick(self, tick):
        self.last_price = tick['last_price']
        self.r.set(f'last_price-{self.symbol}', self.last_price)
        self.last_timestamp = tick['timestamp']
        'make this tz aware if not'
        if(not self.last_timestamp.tzinfo):
            self.last_timestamp = pd.Timestamp(
                self.last_timestamp, tz='Asia/Kolkata')
        for ohlck in self.ohlcs:
            self.ohlcs[ohlck].feed_price(self.last_timestamp, self.last_price)
