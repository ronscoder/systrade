'''
's02 based on fib retracement for entry'
'''
from libs.s00 import S00
from kiteconnect import KiteConnect
from libs.values import EntrySignal, PostEntrySignal, PostEntryActions
# from libs.calculation import Calculation
from libs.calculationfft import Calculation
from libs.candles import CandleUtility


class S02(S00):
    def __init__(self, signature='S02') -> None:
        super().__init__(signature)

    def entry_signal(self, calcdata) -> EntrySignal:
        idxsymbol = calcdata['symbol']
        calc: Calculation = calcdata['calc']['LTF']
        tftype = calcdata['tftype']

        ohlcs = calc.ohlcs

        cu = CandleUtility(ohlcs)
        # s = EntrySignal(idxsymbol=idxsymbol, stoploss=None,
        #                 direction=None, entrymethod='', entrycode='')

        rlevel = calc.get_retracement_level()

        if(rlevel in [1,2,3] and (cu.isBull()) and calc.supslope > 0.1):
            s = EntrySignal(idxsymbol=idxsymbol, stoploss=min(ohlcs.iloc[-3:-1]['Close']),
                        direction=1, entrymethod=f'S02 - Uptrend - retracement level {rlevel}', entrycode=self.signature)
            return s

        if(rlevel in [1,2,3] and (cu.isBear()) and calc.resslope < -0.1):
            s = EntrySignal(idxsymbol=idxsymbol, stoploss=min(ohlcs.iloc[-3:-1]['Close']),
                        direction=-1, entrymethod=f'S02 - Downtrend - retracement level {rlevel}', entrycode=self.signature)

            return s
            
        if(rlevel > 4 and rlevel < 7 and (cu.isBull()) and calc.resslope < -0.1):
            s = EntrySignal(idxsymbol=idxsymbol, stoploss=min(ohlcs.iloc[-3:-1]['Close']),
                        direction=1, entrymethod=f'S02 - retracement failed downbounce {rlevel}', entrycode=self.signature)
            return s

        if(rlevel > 4 and rlevel < 7 and (cu.isBear()) and calc.supslope > 0.1):
            'retracement failed'
            s = EntrySignal(idxsymbol=idxsymbol, stoploss=min(ohlcs.iloc[-3:-1]['Close']),
                        direction=-1, entrymethod=f'S02 - retracement failed upbounce {rlevel}', entrycode=self.signature)

            return s

    
    def postentry_signal(self, calcdata) -> PostEntrySignal:
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