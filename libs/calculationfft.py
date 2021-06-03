import datetime
from libs.configs import getConfig
import trendln
import numpy as np
import pandas as pd


class Calculation:
    def __init__(self, maxn_points=None, n_recalc_period=5, offset=3) -> None:
        self.last_price = None
        self.timestamp = None
        self.ohlcs: pd.DataFrame = None
        self.token = None
        self.offset = offset
        self.n_recalc_period = n_recalc_period
        self.n_since_calc = -1
        if(maxn_points):
            self.maxn_points = maxn_points
        else:
            self.maxn_points = int(getConfig('maxn_points'))
        self.psup = self.pres = None
        self.shistory = []
        self.rhistory = []
        self.cbs = set()
        self.maximas = []
        self.minimas = []
        self.maxima = None
        self.minima = None
        self.supslope = None
        self.resslope = None
        self.retracement_levels = None
        self.yt = None

    def subscribe(self, cb):
        self.cbs.add(cb)

    def calc_trendln(self):
        offset = self.offset
        if(len(self.ohlcs) < self.offset):
            offset = 0
        datapoints = self.ohlcs.iloc[-(self.maxn_points + offset):-offset]
        if(datapoints is None):
            return
        n = len(datapoints)
        acc = int(getConfig('ACCURACY'))
        try:
            Yw = np.fft.rfft(datapoints['Close'])
            yt = np.fft.irfft(Yw[:3], n=len(datapoints))
            self.yt = (datapoints.index, yt)
            mins, maxs = trendln.calc_support_resistance(
                yt, accuracy=acc)
        except Exception as ex:
            print('[ERROR]', ex.__str__())
            return

        (minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs,
                                                   pmax, maxtrend, maxwindows) = mins, maxs
        'also shift the center to right by n'
        if(not np.nan in pmin):
            self.psup = np.poly1d([pmin[0], pmin[1]+pmin[0]*(n+offset)])
            self.supslope = pmin[0]
        if(not np.nan in pmax):
            self.pres = np.poly1d([pmax[0], pmax[1]+pmax[0]*(n+offset)])
            self.resslope = pmax[0]

        if(maximaIdxs):
            self.maximas = [(datapoints.index[x], datapoints.iloc[x]['Close'])
                            for x in maximaIdxs]
        if(minimaIdxs):
            self.minimas = [(datapoints.index[x], datapoints.iloc[x]['Close'])
                            for x in minimaIdxs]

        if(self.maximas and self.supslope):
            if(self.supslope > 0):
                'get the last prominent maxima '
                maxid = maximaIdxs[-1]
                self.maxima = datapoints.index[maxid], datapoints.iloc[maxid]['Close']
                'if there are maximas in close proximity, take the max'
                for r in range(maxid-3, maxid):
                    if(r in maximaIdxs and datapoints.iloc[r]['Close'] > self.maxima[1]):
                        self.maxima = datapoints.index[r], datapoints.iloc[r]['Close']
                        maxid = r
                if(self.minimas):
                    'for minima preceeding the maxima'
                    minimaIdxs2 = [x for x in minimaIdxs if x < maxid]
                    if(minimaIdxs2):
                        minid = minimaIdxs2[-1]
                        self.minima = datapoints.index[minid], datapoints.iloc[minid]['Close']
                        for r in range(minid-3, minid):
                            if(r in minimaIdxs2 and datapoints.iloc[r]['Close'] < self.minima[1]):
                                self.minima = datapoints.index[r], datapoints.iloc[r]['Close']
                                minid = r

                if(self.maxima and self.minima):
                    'calculate the fib retracement levels'
                    fib_ratios = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
                    self.retracement_levels = [self.maxima[1]-(
                        self.maxima[1]-self.minima[1])*ratio for ratio in fib_ratios]

        if(self.minimas and self.resslope):
            if(self.resslope < 0):
                minid = minimaIdxs[-1]
                self.minima = datapoints.index[minid], datapoints.iloc[minid]['Close']
                for r in range(minid-3, minid):
                    if(r in minimaIdxs and datapoints.iloc[r]['Close'] < self.minima[1]):
                        self.minima = datapoints.index[r], datapoints.iloc[r]['Close']
                        minid = r
                if(self.maximas):
                    'for minima preceeding the maxima'
                    maximaIdxs2 = [x for x in maximaIdxs if x < minid]
                    if(maximaIdxs2):
                        maxid = maximaIdxs2[-1]
                        self.maxima = datapoints.index[maxid], datapoints.iloc[maxid]['Close']
                        for r in range(maxid-3, maxid):
                            if(r in maximaIdxs2 and datapoints.iloc[r]['Close'] < self.maxima[1]):
                                self.maxima = datapoints.index[r], datapoints.iloc[r]['Close']
                                maxid = r
                if(self.maxima and self.minima):
                    'calculate the fib retracement levels'
                    fib_ratios = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
                    '            0  1      2      3    4       5     6   7' 
                    # fib_ratios.reverse()
                    # import pdb; pdb.set_trace()
                    self.retracement_levels = [self.minima[1]+(
                        self.maxima[1]-self.minima[1])*ratio for ratio in fib_ratios]

    def get_retracement_level(self):
        if(self.retracement_levels):
            return np.digitize(self.ohlcs.iloc[-1]['Close'], self.retracement_levels)

    def get_sr(self, offset=0):
        sup = res = None
        if(self.psup):
            sup = self.psup(offset)
        if(self.pres):
            res = self.pres(offset)
        return (sup, res)

    def update_supres(self):
        if(self.psup):
            self.psup = np.poly1d(
                [self.psup.c[0], self.psup.c[1] + self.psup.c[0]*self.n_since_calc])
            s = self.psup(0)
            self.shistory.append(
                (self.ohlcs.index[-1], dict(value=s, slope=self.psup.c[0])))
            print(datetime.datetime.time(
                self.shistory[-1][0]), 'support:', self.shistory[-1][1])
        if(self.pres):
            self.pres = np.poly1d(
                [self.pres.c[0], self.pres.c[1] + self.pres.c[0]*self.n_since_calc])
            r = self.pres(0)
            self.rhistory.append(
                (self.ohlcs.index[-1], dict(value=r, slope=self.pres.c[0])))
            print(datetime.datetime.time(
                self.rhistory[-1][0]), 'resistance:', self.rhistory[-1][1])

    def calc(self):
        'min 4 sticks required'
        if(self.ohlcs is None):
            return
        length = len(self.ohlcs)
        acc = int(getConfig('ACCURACY'))
        if(length < (acc+acc/2+1)):
            return
        else:
            self.calc_trendln()

    def on_data(self, data):
        'data will come on every candle update'
        self.last_price = data['last_price']
        self.timestamp = data['timestamp']
        self.ohlcs = data['ohlcs']
        self.token = data['token']
        self.n_since_calc += 1
        if(self.n_since_calc == 0):
            self.calc()
        else:
            if(self.n_since_calc >= self.n_recalc_period):
                self.calc()
                self.n_since_calc = 0
            else:
                print('n_since_calc:',
                      f'{self.n_since_calc}/{self.n_recalc_period}')
        'shift psup/res'
        self.update_supres()

        # for cb in self.cbs:
        #     cb()
