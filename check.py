import datetime
import os
from libs.instruments import Instrument, get_instruments

insts = get_instruments()

token = 256265
symbol = 'NIFTY 50'

inst = Instrument('NIFTY 50', 256265, 5, 15)


'1. init history'
import yfinance as yf

import pickle
fname = 'testdata/^NSEI-2021-05-31-5m'
if(os.path.exists(fname)):
    with open(fname, 'rb') as ff:
        data = pickle.load(ff)
else:
    data = yf.download('^NSEI', period='1d', interval='5m')
    if(data is not None):
        with open(fname, 'wb') as ff:
            pickle.dump(data, ff)

histdata = data.iloc[:20]
testdata = data.iloc[20:]

inst.set_ohlcs(5, histdata)

import random
import time
tickinteval = 1
ltfmindelta = datetime.timedelta(minutes=5)
for i, row in testdata.iterrows():
    i = i.replace(tzinfo=None)
    ticks = {'instrument_token': token, 'tradingsymbol': symbol,
                'timestamp': i, 'last_price': row['Open']}
    inst.feed_tick(ticks)
    time.sleep(tickinteval)
    ifh = random.randint(0, 1)
    ticks = {'instrument_token': token, 'tradingsymbol': symbol, 'timestamp': i + ltfmindelta /
                4, 'last_price': row['High'] if ifh else row['Low']}
    inst.feed_tick(ticks)
    time.sleep(tickinteval)
    ticks = {'instrument_token': token, 'tradingsymbol': symbol, 'timestamp': i + ltfmindelta /
                2, 'last_price': row['Low'] if ifh else row['High']}
    inst.feed_tick(ticks)
    time.sleep(tickinteval)
    ticks = {'instrument_token': token, 'tradingsymbol': symbol,
                'timestamp': i+ltfmindelta, 'last_price': row['Close']}
    inst.feed_tick(ticks)
    time.sleep(tickinteval)




