from requests.api import get
from libs.values import EntrySignal, PostEntrySignal
from libs.instruments import get_instruments
from libs.orderapi import Orderapi
from libs.options import get_nifty_contracts
from kiteconnect import KiteConnect
from libs.pubsub import get_ps_1

# indices = [x for x in get_instruments() if x['type'] == 'INDEX']

from libs.s01 import S01

orderapi = Orderapi()
r = get_ps_1()


class OptionNifty:
    def __init__(self) -> None:
        self.contracts = get_nifty_contracts()
        self.s = S01()

    def start(self):
        self.s.subscribe(['NIFTY 50'], cb_entry=self.entry,
                         cb_postentry=self.postentry)

    def entry(self, signal: EntrySignal):
        otype = 'ce' if signal.direction == 1 else 'pe'
        contracts = sorted([x for x in self.contracts[otype] if x[1] <= 500], key=lambda x: x[1], reverse=True)
        # contracts = sorted([x for x in contracts['ce'] if x[1] <= 500], key=lambda x: x[1], reverse=True)
        # print(contracts)
        instsymbol = contracts[0][0]
        idxsymbol = signal.idxsymbol
        idxstoploss = signal.stoploss
        qty = 75
        r.hset('inst_symbolof', {idxsymbol: instsymbol})
        ltp = orderapi.kite.ltp('NFO:'+instsymbol)['NFO:'+instsymbol]['last_price']
        r.hset('pl', {instsymbol: {'entry': ltp}})
        'execute order'
        'stoploss not known, unless specified risk-reward ratio'
        # orderapi.place_idx_order(signal.txntype, inst_symbol=instsymbol, qty=qty,
        #                          idxsymbol=idxsymbol, idxstoploss=idxstoploss, exchange=KiteConnect.EXCHANGE_NSE)

    def postentry(self, signalinfo: PostEntrySignal):
        print('execute post-action')
        idxsymbol = signalinfo.idxsymbol
        print(f'post entry test {idxsymbol}')
        instsymbol = r.hget('inst_symbolof', idxsymbol)
        ltp = orderapi.kite.ltp('NFO:'+instsymbol)['NFO:'+instsymbol]['last_price']
        pl = r.hget('pl', instsymbol)
        pl['exit'] = ltp
        r.hset('pl', {instsymbol: pl})
        # orderapi.exit_order_m(instsymbol, action=signalinfo.action)


if(__name__ == '__main__'):
    OptionNifty().start()
