from kiteconnect.connect import KiteConnect as KC
from libs.pubsub import get_ps_1
from libs.values import PostEntrySignal, PostEntryActions
from libs.init_kite import KiteWrapper


class Orderapi:
    def __init__(self) -> None:
        self.kite = KiteWrapper().kite
        self.r = get_ps_1()

    def place_co(self, instsymbol, txnType, qty, stoploss):
        kite = self.kite
        params = dict(variety=kite.VARIETY_CO, exchange=kite.EXCHANGE_NSE, tradingsymbol=instsymbol, transaction_type=txnType,
                      quantity=qty, product=kite.PRODUCT_CO, order_type=kite.ORDER_TYPE_MARKET, price=None, validity=None, trigger_price=stoploss)
        updates = {}
        updates['status'] = 'init'
        updates['order_id'] = None
        self.r.hset('positions', {instsymbol: dict(params=params, updates=updates)})
        order_id = self.kite.place_order(**params)
        if(order_id):
            position = self.r.hget('positions', instsymbol)
            position['updates']['order_id'] = order_id
            position['updates']['status'] = 'order placed'
            self.r.hset('positions', {instsymbol: position})
        else:
            print('order failed', params)

    def exit_order(self, instsymbol, action: PostEntryActions):
        # import pdb; pdb.set_trace()
        position = self.r.hget('positions', instsymbol)
        if(position is None):
            print('Error: no position exists', instsymbol, action.name)
            return
        if(action == PostEntryActions.exit_all):
            if(position['params']['variety'] == KC.VARIETY_CO):
                self.kite.exit_order(
                    variety=position['params']['variety'], order_id=position['updates']['counter_order_id'])
            else:
                if(position['updates'].get('counter_order_id', None) is not None):
                    'for order with counter order'
                    self.kite.modify_order(
                        variety=position['params']['variety'], order_id=position['updates']['counter_order_id'], order_type=KC.ORDER_TYPE_MARKET)
                else:
                    'single leg position'
                    self.exit_order_m(instsymbol=instsymbol, action=action)
        if(action == PostEntryActions.update_sl):
            'TODO '

    def place_idx_order(self, txntype, inst_symbol, qty, idxsymbol, idxstoploss, exchange):
        'The exit order should be taken care by manual codes'
        params = dict(variety=KC.VARIETY_REGULAR, exchange=exchange, tradingsymbol=inst_symbol,
                      transaction_type=txntype, quantity=qty, product=KC.PRODUCT_MIS, order_type=KC.ORDER_TYPE_MARKET)
        updates = {}
        updates['status'] = 'init'
        updates['order_id'] = None
        updates['idxsymbol'] = idxsymbol
        updates['idxstoploss'] = idxstoploss
        self.r.hset('positions', {inst_symbol: dict(params=params, updates=updates)})
        order_id = self.kite.place_order(**params)
        if(order_id):
            print('order placed', order_id)
            position = self.r.hget('positions', inst_symbol)
            position['updates']['order_id'] = order_id
            position['updates']['status'] = 'order placed'
            self.r.hset('positions', {inst_symbol: position})
        else:
            print('order failed', params)
        'stoploss? need to monitor and trigger, by ordermgr'

    def exit_order_m(self, instsymbol, action: PostEntryActions):
        buyparams = self.r.hget('positions', instsymbol)
        if(buyparams is None):
            print('Error: no position exists', instsymbol, action.name)
            return
        txntype = KC.TRANSACTION_TYPE_BUY if buyparams['params'][
            'transaction_type'] == KC.TRANSACTION_TYPE_SELL else KC.TRANSACTION_TYPE_SELL
        params = dict(variety=KC.VARIETY_REGULAR, exchange=buyparams['params']['exchange'], tradingsymbol=instsymbol, transaction_type=txntype,
                      quantity=buyparams['params']['quantity'], product=KC.PRODUCT_MIS, order_type=KC.ORDER_TYPE_MARKET)

        order_id = self.kite.place_order(**params)
        if(order_id):
            buyparams['updates']['counter_order_id'] = order_id
            self.r.hset('positions', {instsymbol: buyparams})
        else:
            print('order failed', params)
        'stoploss? need to monitor and trigger, by ordermgr'

    def place_mis_order_withsl(self, txntype, inst_symbol, qty, stoploss):
        params = dict(variety=KC.VARIETY_REGULAR, exchange=KC.EXCHANGE_NSE, tradingsymbol=inst_symbol,
                      transaction_type=txntype, quantity=qty, product=KC.PRODUCT_MIS, order_type=KC.ORDER_TYPE_MARKET)
        updates = {}
        updates['status'] = 'init'
        updates['stoploss'] = stoploss
        updates['order_id'] = None
        self.r.hset('positions', {inst_symbol: dict(params=params, updates=updates)})
        order_id = self.kite.place_order(**params)
        if(order_id):
            'order placed'
            position = self.r.hget('positions', inst_symbol)
            position['updates']['order_id'] = order_id
            position['updates']['status'] = 'order placed'
            self.r.hset('positions', {inst_symbol: position})
        else:
            print('order failed', params)

    def _place_counter_mis_slorder(self, inst_symbol):
        position = self.r.hget('positions', inst_symbol)
        if(position is None):
            print('Error no position for ', inst_symbol)
        txntype = KC.TRANSACTION_TYPE_BUY if position['params'][
            'transaction_type'] == KC.TRANSACTION_TYPE_SELL else KC.TRANSACTION_TYPE_SELL
        params = dict(variety=KC.VARIETY_REGULAR, exchange=KC.EXCHANGE_NSE, tradingsymbol=inst_symbol, transaction_type=txntype,
                      quantity=position['params']['quantity'], product=KC.PRODUCT_MIS, order_type=KC.ORDER_TYPE_SLM, trigger_price=position['updates']['stoploss'])
        counter_order_id = self.kite.place_order(**params)
        if(counter_order_id):
            position['updates']['counter_order_id'] = counter_order_id
            self.r.hset('positions', {inst_symbol: position})
