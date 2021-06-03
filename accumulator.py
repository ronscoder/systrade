import datetime

from yfinance.multi import download
from libs.configs import getConfig
from typing import Dict
from libs.pubsub import get_ps_1, get_ps_2
from libs.instruments import get_instruments, Instrument
from libs.values import PCONSTS
from libs.xprint import fixprint
import yfinance as yf
import pandas as pd
'All data will be stored and managed by this module. Publishing data updates'

r = get_ps_1()

sub_channels = [x.name for x in [PCONSTS.connection, PCONSTS.ticks]]


class DataSub:
    def __init__(self) -> None:
        self.inst_list = get_instruments()
        self.instruments: Dict[int, Instrument] = {x['token']: Instrument(
            x['symbol'], x['token'], ltf_min=5, htf_min=15) for x in self.inst_list}  # TODO tfs from config
        self.plen = 0
        self.r = get_ps_1()
        self.init_history()

    def init_history(self):
        for token in self.instruments:
            inst = self.instruments[token]
            print(f'setting history {inst.symbol}')
            ltf_inst = self.r.get(f'INSTRUMENT-{inst.symbol}-OHLC-{inst.ltf_min}')
            ifdownload = ltf_inst is None
            if(download):
                print(f'INSTRUMENT-{inst.symbol}-OHLC-{inst.ltf_min}: None? {ltf_inst is None}')
            if(not ltf_inst is None):
                lastIdx = ltf_inst['ohlcs'].index[-1]
                lastIdx = lastIdx.replace(tzinfo=None)
                ifdownload = lastIdx + datetime.timedelta(minutes=inst.ltf_min) < datetime.datetime.now()
                if(ifdownload):
                    print(f'last index: {lastIdx}, tf: {inst.ltf_min}, current: {datetime.datetime.now()}')
            if(ifdownload):
                # import pdb; pdb.set_trace()
                print(f'download history {inst.symbol}')
                'TODO use an abstract api for history download'
                data = yf.download([x['ysymbol'] for x in self.inst_list if x['token']
                                                    == token][0], period='1d', interval=f'{inst.ltf_min}m')
                if(not data is None):
                    inst.set_ohlcs(inst.ltf_min, data)
            'TODO resample for HTF'

    def sub_handler(self, channel, data):
        # print(channel, data)
        if(channel == PCONSTS.connection.name):
            # print(data)
            if(data == PCONSTS.connected.name):
                print('on connected')
                self.init_history()

        if(channel == PCONSTS.ticks.name):
            ticks = data
            for tick in ticks:
                token = tick['instrument_token']
                'NOTE: When acc is running, it will just keep appending new tick data. During test, this should be restarted'
                txt = f'{self.instruments[token].symbol}: {tick["last_price"]}'
                self.plen = len(txt)
                fixprint(txt)
                # import pdb; pdb.set_trace()
                self.instruments[token].feed_tick(tick)


if __name__ == "__main__":
    datasub = DataSub()
    # import pdb; pdb.set_trace()
    r.subscribe(sub_channels, datasub.sub_handler)
    # t1 = datetime.datetime.now()
    # t2 = t1 + datetime.timedelta(minutes=6)
    # datasub.sub_handler(PCONSTS.ticks.name, [{'instrument_token': 256265, 'last_price': 15300, 'timestamp': t1}])
    # datasub.sub_handler(PCONSTS.ticks.name, [{'instrument_token': 256265, 'last_price': 15301, 'timestamp': t2}])
