'''
abstract class for all strategies
Dependencies: 
key: POSITION-[symbol]
'''
from libs.values import EntrySignal, PostEntrySignal, PostEntryActions
from typing import List
from libs.pubsub import get_ps_1


class S00:
    def __init__(self, signature) -> None:
        self.cb_entry = None
        self.cb_postentry = None
        self.symbols = []
        self.entry_info: EntrySignal = None
        self.signature = signature
        self.r = get_ps_1()

    def entry_signal(self, calcdata)->EntrySignal:
        'overwrite this'
        pass

    def postentry_signal(self, calcdata)->PostEntrySignal:
        'Overwrite. This could be to exit or update exit order'
        pass

    def _detect_signal(self, channel, calcdata):
        'Avoid detection if existing position for the symbol'
        print('detecting signals...')
        idxsymbol = calcdata['symbol']
        instsymbol = self.r.hget('inst_symbolof', idxsymbol)
        position = None
        if(instsymbol):
            position = self.r.hget('positions', instsymbol)
        if(not position):
            self.entry_info = self.entry_signal(calcdata)
            if(self.entry_info):
                self.r.lpush(f'entry-history', self.entry_info)
                self.r.publish(f'entry-{instsymbol}', self.entry_info)
                self.cb_entry(self.entry_info)
        else:
            self.entry_info = self.r.get(f'entry-{instsymbol}')
            if(self.entry_info.entrycode == self.signature):
                postinfo = self.postentry_signal(calcdata)
                if(postinfo):
                    self.r.lpush(f'postentry-history', postinfo)
                    self.r.publish(f'postentry-{instsymbol}', postinfo)
                    self.cb_postentry(postinfo)

    def subscribe(self, idxsymbols: List, cb_entry, cb_postentry):
        'Call this after declaration'
        self.cb_entry = cb_entry
        self.cb_postentry = cb_postentry
        self.symbols = idxsymbols
        'subscribe to calculations'
        'This will happen on ohlc updates only'
        self.r.subscribe([f'CALC-{symbol}-*' for symbol in idxsymbols], self._detect_signal)
        'Can also subscribe to ticks'