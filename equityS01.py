from kiteconnect.connect import KiteConnect
from libs.values import EntrySignal, PostEntrySignal
from libs.instruments import get_instruments
from libs.orderapi import Orderapi
from libs.pubsub import get_ps_1

equityInsts = [x for x in get_instruments() if x['type'] == 'EQUITY']
'TODO undo this'
from libs.s01 import S01
# from libs.stest import S01

orderapi = Orderapi()

r = get_ps_1()


def entry(signal: EntrySignal):
    'execute order'
    idxsymbol = signal.idxsymbol
    txtType = KiteConnect.TRANSACTION_TYPE_BUY if signal.direction == 1 else KiteConnect.TRANSACTION_TYPE_SELL
    stoploss = signal.stoploss
    instsymbol = idxsymbol #for equity same
    r.hset('inst_symbolof', {instsymbol: instsymbol})
    'define qty'
    qty = 1
    print('Entry', signal)
    orderapi.place_co(instsymbol=instsymbol,
                    txnType=txtType, qty=qty, stoploss=stoploss)


def postentry(signalinfo: PostEntrySignal):
    'execute post-action'
    idxsymbol = signalinfo.idxsymbol
    instsymbol = r.hget('inst_symbolof', idxsymbol)
    print('postentry', signalinfo)
    orderapi.exit_order(instsymbol=instsymbol, action=signalinfo.action)

if(__name__ == '__main__'):
    s01 = S01()
    s01.subscribe([x['symbol'] for x in equityInsts],
                cb_entry=entry, cb_postentry=postentry)
