from requests.api import get
from libs.values import EntrySignal, PostEntrySignal
from libs.instruments import get_instruments
from libs.orderapi import Orderapi
from libs.options import get_nifty_contracts
from kiteconnect import KiteConnect
from libs.pubsub import get_ps_1
import datetime
# indices = [x for x in get_instruments() if x['type'] == 'INDEX']

from libs.s02_retracement import S02

orderapi = Orderapi()
r = get_ps_1()


class OptionNifty:
    def __init__(self) -> None:
        self.contracts = get_nifty_contracts()
        self.s = S02()

    def start(self):
        self.s.subscribe(['NIFTY 50'], cb_entry=self.entry,
                         cb_postentry=self.postentry)

    def entry(self, signal: EntrySignal):
        print('executing entry')
        otype = 'ce' if signal.direction == 1 else 'pe'
        contracts = sorted([x for x in self.contracts[otype]
                            if x[1] <= 50], key=lambda x: x[1], reverse=True)
        instsymbol = contracts[0][0]

        idxsymbol = signal.idxsymbol
        r.hset('inst_symbolof', {idxsymbol: instsymbol})

        idxstoploss = signal.stoploss
        qty = 75
        print(datetime.datetime.now(), signal)
        # orderapi.place_idx_order(KiteConnect.TRANSACTION_TYPE_BUY, inst_symbol=instsymbol, qty=qty,
        #                          idxsymbol=idxsymbol, idxstoploss=idxstoploss, exchange=KiteConnect.EXCHANGE_NFO)

    def postentry(self, signalinfo: PostEntrySignal):
        print('executing post-action')

        idxsymbol = signalinfo.idxsymbol
        print(f'post entry test {idxsymbol}')

        instsymbol = r.hget('inst_symbolof', idxsymbol)

        # orderapi.exit_order_m(instsymbol, action=signalinfo.action)


if(__name__ == '__main__'):
    OptionNifty().start()
