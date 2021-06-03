from libs.values import PostEntryActions
from libs.init_kite import KiteWrapper
from libs.pubsub import get_ps_1

r = get_ps_1()

kite = KiteWrapper().kite


# import pdb; pdb.set_trace()
from libs.orderapi import Orderapi

o = Orderapi()
# o.place_mis_order(kite.TRANSACTION_TYPE_BUY, 'TATAPOWER', 1, 105)
# o.exit_order('TATAPOWER', action= PostEntryActions.exit_all)

# o.place_mis_order(kite.TRANSACTION_TYPE_SELL, 'TATAPOWER', 1, 109)
# o.exit_order('TATAPOWER', action= PostEntryActions.exit_all)

# o.place_co(sym, kite.TRANSACTION_TYPE_SELL, 1, 109)
# o.exit_order('TATAPOWER', action= PostEntryActions.exit_all)

# o.place_idx_order(kite.TRANSACTION_TYPE_SELL, 'SUNPHARMA', 1, 'SUNPHARMA', 702, kite.EXCHANGE_NSE)
# kite.startrms()
r.r.delete('orders')
print('placing order')
o.place_co('TATAPOWER', kite.TRANSACTION_TYPE_BUY, 1, 104)
o.exit_order('TATAPOWER', PostEntryActions.exit_all)