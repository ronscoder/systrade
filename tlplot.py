import trendln
from libs.pubsub import get_ps_1
import matplotlib.pyplot as plt
from custom_package import candle
import numpy as np
import datetime
from libs.values import isNonTradingDay
import os
import pickle
import yfinance as yf
import numpy as np

ohlcs = None
testday = '06-01'
testdaystr = f'2021-{testday}'
fname = f'testdata/^NSEI-{testdaystr}-5m'
testdt = datetime.datetime.strptime(testdaystr, '%Y-%m-%d').date()
if(isNonTradingDay(testdt)):
    print('Non trading day')
else:
    if(os.path.exists(fname)):
        with open(fname, 'rb') as ff:
            ohlcs = pickle.load(ff)
    else:
        print('downloading...')
        ohlcs = yf.download('^NSEI', start=testdt, end=testdt +
                            datetime.timedelta(days=1), interval='5m')
        if(not ohlcs is None):
            with open(fname, 'wb') as ff:
                pickle.dump(ohlcs, ff)

n_test = 10
n_test_idx = ohlcs.index[-n_test]

def calc(data):
    mins, maxs = trendln.calc_support_resistance(data, accuracy=2)
    return mins, maxs

def plot(data, mins, maxs, ax):
    (minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs,
                                               pmax, maxtrend, maxwindows) = mins, maxs
    psup = np.poly1d([pmin[0], pmin[1]])
    pres = np.poly1d([pmax[0], pmax[1]])
    ax.plot(ohlcs.index, data)
    # ax.axvline(n_test_idx)
    #     ax.plot(ohlcs.index, list(psup(range(len(ohlcs)))), 'g')
    #     ax.plot(ohlcs.index, list(pres(range(len(ohlcs)))), 'r')
    'ignore the min/max if on the last candle'
    ax.plot(ohlcs.index[maximaIdxs], ohlcs.iloc[maximaIdxs].Close, 'ok')
    ax.plot(ohlcs.index[minimaIdxs], ohlcs.iloc[minimaIdxs].Close, 'ob')

    #     pres1 = np.poly1d((maxtrend[0][1][0], maxtrend[0][1][1]))
    #     ax.plot(ohlcs.index[maxtrend[0][0]], pres1(maxtrend[0][0]))

    #     pres2 = np.poly1d((maxtrend[-1][1][0], maxtrend[-1][1][1] + maxtrend[-1][1][4]))
    #ax.plot(ohlcs.index[maxtrend[1][0]], pres2(maxtrend[1][0]))
    #     ax.plot(ohlcs.index, pres2(range(len(ohlcs))))
    # 'find the latest extremas'
    # i=1
    # minid = minimaIdxs[-1]
    # while(ohlcs.iloc[minimaIdxs[-(i+1)]].Close < ohlcs.iloc[minimaIdxs[-i]].Close and (i+1 < len(minimaIdxs))):
    #     minid = minimaIdxs[-(i+1)]
    #     i+=1
    # i=1
    # maxid = maximaIdxs[-1]
    # while(ohlcs.iloc[maximaIdxs[-(i+1)]].Close > ohlcs.iloc[maximaIdxs[-i]].Close and (i+1 < len(maximaIdxs))):
    #     maxid = maximaIdxs[-(i+1)]
    #     i+=1

    # ax.plot(ohlcs.index[[minid,maxid]], [ohlcs.iloc[minid].Close, ohlcs.iloc[maxid].Close])

    # ax.hlines(y=[ohlcs.iloc[minid].Close, ohlcs.iloc[maxid].Close], xmin=ohlcs.index[minid], xmax=ohlcs.index[maxid])

    # fib_ratios = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
    # levels = [(ohlcs.iloc[maxid].Close-ohlcs.iloc[minid].Close)*ratio for ratio in fib_ratios]
    # ax.hlines(y=[ohlcs.iloc[maxid].Close-x for x in levels], xmin=ohlcs.index[minid], xmax=ohlcs.index[maxid])


ax1 = plt.subplot(211)
mins, maxs = calc(ohlcs.Close)
candle.timeplot(ax1, ohlcs)
plot(ohlcs.Close, mins, maxs, ax1)

n = len(ohlcs)
datafft = np.fft.rfft(ohlcs.Close)
dataifft = np.fft.irfft(datafft, n)
mins, maxs = calc(dataifft)
ax2 = plt.subplot(212)
plot(dataifft, mins, maxs, ax2)
plt.show()