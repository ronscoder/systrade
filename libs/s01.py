'''
's01 strategy'
1. simple big sticks

'''
from typing import List
from libs.s00 import S00
from libs.pubsub import get_ps_1
from libs.values import PostEntryActions
from kiteconnect import KiteConnect
from libs.values import EntrySignal, PostEntrySignal
import datetime
# from libs.calculation import Calculation
from libs.calculationfft import Calculation
from libs.candles import CandleUtility

r = get_ps_1()


class S01(S00):
    def __init__(self, signature='S01-1') -> None:
        super().__init__(signature=signature)

    def entry_signal(self, calcdata) -> EntrySignal:
        print('check for entry signal...')
        idxsymbol = calcdata['symbol']
        calc: Calculation = calcdata['calc']['LTF']
        tftype = calcdata['tftype']
        ohlcs = calc.ohlcs
        cu = CandleUtility(ohlcs)
        # s = None
        'S01-1: triangulation'
        if(calc.rhistory and calc.shistory):
            rslope = calc.rhistory[-1][1]['slope']
            sslope = calc.shistory[-1][1]['slope']
            dslope = rslope - sslope
            if(dslope < -0.5):
                'if bullish candle'
                if(cu.isBull()):
                    s = EntrySignal(idxsymbol=idxsymbol, stoploss=ohlcs.iloc[-1]['Low'],
                                    direction=1, entrymethod='Triangulation/Bull', entrycode=self.signature)
                    # s.direction = 1
                    # s.stoploss = ohlcs[-1]['Low']
                    # s.entrycode = 'S01-1'
                    # s.entrymethod = 'Triangulation/Bull'
                    # r.hset(
                    #     f'entry_signal_time-{idxsymbol}', {datetime.datetime.now(): s})
                    return s
            if(dslope > -0.5):
                'if bullish candle'
                if(cu.isBear()):
                    s = EntrySignal(idxsymbol=idxsymbol, stoploss=ohlcs.iloc[-1]['High'],
                                    direction=-1, entrymethod='Triangulation/Bull', entrycode=self.signature)
                    # s.direction = -1
                    # s.stoploss = ohlcs[-1]['High']
                    # s.entrycode = 'S01-1'
                    # s.entrymethod = 'Triangulation/Bull'
                    # r.hset(
                    #     f'entry_signal_time-{idxsymbol}', {datetime.datetime.now(): s})
                    return s

    def postentry_signal(self, calcdata) -> PostEntrySignal:
        # if(self.entry_info)
        idxsymbol = calcdata['symbol']
        calc: Calculation = calcdata['calc']['LTF']
        tftype = calcdata['tftype']

        ohlcs = calc.ohlcs
        cu = CandleUtility(ohlcs)
        direction = self.entry_info.direction
        if(cu.is_price_weak(direction=direction)):
            s = PostEntrySignal(idxsymbol=idxsymbol,
                                action=PostEntryActions.exit_all)
            return s
