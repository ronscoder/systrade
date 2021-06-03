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
import time
r = get_ps_1()


class S01(S00):

    def __init__(self, signature='S01-Test') -> None:
        super().__init__(signature)

    def entry_signal(self, calcdata) -> EntrySignal:
        print('check for entry signal...')
        idxsymbol = calcdata['symbol']
        calc: Calculation = calcdata['calc']['LTF']
        tftype = calcdata['tftype']
        ohlcs = calc.ohlcs
        cu = CandleUtility(ohlcs)
        s = EntrySignal(idxsymbol='AXISBANK', stoploss=730,
                        direction=1, entrymethod='Triangulation/Bull', entrycode=self.signature)
        return s

    def postentry_signal(self, calcdata) -> PostEntrySignal:
        idxsymbol = calcdata['symbol']
        calc: Calculation = calcdata['calc']['LTF']
        tftype = calcdata['tftype']

        ohlcs = calc.ohlcs
        cu = CandleUtility(ohlcs)
        direction = self.entry_info.direction
        s = PostEntrySignal(idxsymbol='AXISBANK',
                                action=PostEntryActions.exit_all)
        return s
    def _detect_signal(self, channel, calcdata):
        super()._detect_signal(channel, calcdata)

    'TODO: delete this after test'
    def subscribe(self, idxsymbols: List, cb_entry, cb_postentry):
        self.cb_entry = cb_entry
        self.cb_postentry = cb_postentry
        self.symbols = idxsymbols
        self._detect_signal(f'CALC-AXISBANK-LTF', r.get(f'CALC-AXISBANK-LTF'))
        input('continue?')
        # import pdb; pdb.set_trace()
        self._detect_signal(f'CALC-AXISBANK-LTF', r.get(f'CALC-AXISBANK-LTF'))