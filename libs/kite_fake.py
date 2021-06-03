import os
import datetime
import pickle

from libs.configs import getConfig
import time
import random
from libs.pubsub import get_ps_1
from libs.instruments import get_instruments
import threading
from libs.values import PCONSTS

r = get_ps_1()


class ProxyKiteConnect:
    # Constants
    # Products
    PRODUCT_MIS = "MIS"
    PRODUCT_CNC = "CNC"
    PRODUCT_NRML = "NRML"
    PRODUCT_CO = "CO"
    PRODUCT_BO = "BO"

    # Order types
    ORDER_TYPE_MARKET = "MARKET"
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_SLM = "SL-M"
    ORDER_TYPE_SL = "SL"

    # Varities
    VARIETY_REGULAR = "regular"
    VARIETY_BO = "bo"
    VARIETY_CO = "co"
    VARIETY_AMO = "amo"

    # Transaction type
    TRANSACTION_TYPE_BUY = "BUY"
    TRANSACTION_TYPE_SELL = "SELL"

    # Validity
    VALIDITY_DAY = "DAY"
    VALIDITY_IOC = "IOC"

    # Exchanges
    EXCHANGE_NSE = "NSE"
    EXCHANGE_BSE = "BSE"
    EXCHANGE_NFO = "NFO"
    EXCHANGE_CDS = "CDS"
    EXCHANGE_BFO = "BFO"
    EXCHANGE_MCX = "MCX"

    # Margins segments
    MARGIN_EQUITY = "equity"
    MARGIN_COMMODITY = "commodity"

    # Status constants
    STATUS_COMPLETE = "COMPLETE"
    STATUS_REJECTED = "REJECTED"
    STATUS_CANCELLED = "CANCELLED"

    # GTT order type
    GTT_TYPE_OCO = "two-leg"
    GTT_TYPE_SINGLE = "single"

    # GTT order status
    GTT_STATUS_ACTIVE = "active"
    GTT_STATUS_TRIGGERED = "triggered"
    GTT_STATUS_DISABLED = "disabled"
    GTT_STATUS_EXPIRED = "expired"
    GTT_STATUS_CANCELLED = "cancelled"
    GTT_STATUS_REJECTED = "rejected"
    GTT_STATUS_DELETED = "deleted"

    def __init__(self) -> None:
        self.kws = ProxyKiteTicker()
        self._orders = []
        print('Fake kite running...')
        
    def startrms(self):
        threading.Thread(target=self.rms).start()

    def on_order_update(self, order):
        r.publish(PCONSTS.order_update.name, order)
        # import pdb; pdb.set_trace()
        r.set('orders', self._orders)

    def _rms(self, channel, ticks):
        sl_orders = [(i, x) for i, x in enumerate(r.get('orders')) if x['status'] not in [
            self.STATUS_COMPLETE] and x['order_type'] == self.ORDER_TYPE_SLM]
        print('sl orders', sl_orders)
        for i, o in sl_orders:
            symbol = o['tradingsymbol']
            last_price = r.get(f'last_price-{symbol}')
            txntype = o['transaction_type']
            if((txntype == self.TRANSACTION_TYPE_BUY and last_price <= o['trigger_price']) or (txntype == self.TRANSACTION_TYPE_SELL and last_price >= o['trigger_price'])):
                
                self._orders[i]['status'] = self.STATUS_COMPLETE
                self.on_order_update(self._orders[i])

    def rms(self):
        print('running rms')
        r.subscribe(PCONSTS.ticks.name, self._rms)

    def positions(self):
        ps = {}
        orders = r.get('orders') or []
        for o in [x for x in orders if x['status'] == self.STATUS_COMPLETE]:
            symbol = o['tradingsymbol']
            qty = o['quantity']
            qty = (-1) * \
                qty if o['transaction_type'] == self.TRANSACTION_TYPE_SELL else qty
            if(symbol not in ps):
                ps[symbol] = {'tradingsymbol': symbol,
                              'instrument_token': o['instrument_token'], 'product': o['product'], 'quantity': qty}
            else:
                ps[symbol]['quantity'] += qty
        return {'net': [ps[x] for x in ps]}

    def orders(self):
        return r.get('orders') or []

    def exit_order(self, variety, order_id, parent_order_id=None):
        'for co only'
        if(not len(self._orders) > 0):
            raise Exception('No position', variety, order_id, parent_order_id)
        if(variety == self.VARIETY_CO):
            idx = [i for i, x in enumerate(
                self._orders) if x['order_id'] == order_id]
            self._orders[idx]['status'] = self.STATUS_COMPLETE
            self.on_order_update(self._orders[idx])
        else:
            raise Exception('Error only for CO', order_id, parent_order_id)

    def _process_order(self):
        order = self._orders[-1]
        time.sleep(0.5)
        self.on_order_update(order)
        time.sleep(0.5)
        if(order['order_type'] == self.ORDER_TYPE_MARKET):
            order['status'] = self.STATUS_COMPLETE
            order['average_price'] = r.get(
                f'last_price-{order["tradingsymbol"]}')
            self.on_order_update(order)
        if(order['product'] == self.PRODUCT_CO):
            corder = {**self._orders[-1]}
            corder['transaction_type'] = self.TRANSACTION_TYPE_BUY if order[
                'transaction_type'] == self.TRANSACTION_TYPE_SELL else self.TRANSACTION_TYPE_SELL
            corder['order_type'] = self.ORDER_TYPE_SLM
            corder['status'] = 'TRIGGER PENDING'
            corder['average_price'] = 0
            corder['parent_order_id'] = order['order_id']
            corder['order_id'] = order['order_id'] + 1
            # import pdb; pdb.set_trace()
            self._orders.append(corder)
            self.on_order_update(corder)

    def place_order(self,
                    variety,
                    exchange,
                    tradingsymbol,
                    transaction_type,
                    quantity,
                    product,
                    order_type,
                    price=None,
                    validity=None,
                    disclosed_quantity=None,
                    trigger_price=None,
                    squareoff=None,
                    stoploss=None,
                    trailing_stoploss=None,
                    tag=None):
        '''
                variety, #variety = ["VARIETY_AMO", "VARIETY_BO", "VARIETY_CO", "VARIETY_REGULAR"] 
                exchange, #exchange = ["EXCHANGE_BFO", "EXCHANGE_BSE", "EXCHANGE_CDS", "EXCHANGE_MCX", "EXCHANGE_NFO", "EXCHANGE_NSE"]
                tradingsymbol, #tradingsymbol = ['INFY','BANKNIFTY20AUGFUT']
                transaction_type, #transaction_type = ["TRANSACTION_TYPE_BUY", "TRANSACTION_TYPE_SELL"]
                quantity, #intented quanity to be traded. Multiples of lot size in case of derivatives
                product, #product = ["PRODUCT_BO", "PRODUCT_CNC", "PRODUCT_CO", "PRODUCT_MIS", "PRODUCT_NRML"]
                order_type, #order_type = ["ORDER_TYPE_LIMIT", "ORDER_TYPE_MARKET", "ORDER_TYPE_SL", "ORDER_TYPE_SLM"] 
                price=None, #offcourse the price at which you want to trade, in multiples of 5 paisa
                validity=None, #validity = ["VALIDITY_DAY", "VALIDITY_IOC"]
                disclosed_quantity=None, # optional. same as quantity or 'None' 
                trigger_price=None, #applicable only for ORDER_TYPE_SL, ORDER_TYPE_SLM and VARIETY_CO's SL leg else 'None'
                squareoff=None, #target price to entry price difference. applicable in case of bracket orders, else 'None'
                stoploss=None, #stop loss to entry price difference. applicable in case of bracket orders, else 'None'
                trailing_stoploss=None, #trailing points in case of a bracket order, else 'None'
                tag=None)   
        '''
        order_id = random.randint(1, 1000)
        token = [x for x in get_instruments() if x['symbol'] ==
                 tradingsymbol][0]['token']
        order = {'account_id': 'YZ7009', 'unfilled_quantity': 0, 'checksum': '', 'placed_by': 'YZ7009', 'order_id': order_id, 'exchange_order_id': '1300000005271142', 'parent_order_id': None, 'status': 'OPEN', 'status_message': None, 'status_message_raw': None, 'order_timestamp': '2021-04-29 10:06:02', 'exchange_update_timestamp': '2021-04-29 10:06:02', 'exchange_timestamp': '2021-04-29 10:06:02', 'variety': variety,
                 'exchange': 'NSE', 'tradingsymbol': tradingsymbol, 'instrument_token': token, 'order_type': order_type, 'transaction_type': transaction_type, 'validity': 'DAY', 'product': product, 'quantity': quantity, 'disclosed_quantity': 0, 'price': price, 'trigger_price': trigger_price, 'average_price': 0, 'filled_quantity': 0, 'pending_quantity': 1, 'cancelled_quantity': 0, 'market_protection': 0, 'meta': {}, 'tag': None, 'guid': '01XasEtN1HNSVNN'}
        self._orders.append(order)
        # print(self._orders)
        time.sleep(1)
        threading.Thread(target=self._process_order).start()
        return order_id


class ProxyKiteTicker:
    MODE_FULL = 'MODE_FULL'

    def __init__(self) -> None:
        self.on_connect = None
        self.on_close = None
        self.on_ticks = None
        self.on_error = None
        self.on_message = None
        self.on_reconnect = None
        self.on_noreconnect = None
        # self.on_order_update = None
        self.tokens = None

    def set_mode(self, mode, tokens):
        ''

    def on_order_update(self, order):
        r.publish(PCONSTS.order_update.name, order)

    def subscribe(self, tokens):
        self.tokens = tokens

    def connect(self):
        self.on_connect(None, None)
        # f = '/Users/ronsair/Workspace/tradesys/TR01_data/SUNPHARMA.NS-15m-5m-2021-05-10.pickle'
        f = '/Users/ronsair/Workspace/tradesys/testdata/SUNPHARMA.NS-2021-05-14-2021-05-18-5m.pickle'
        with open(f, 'rb') as fo:
            data = pickle.load(fo)
        ltfmin = getConfig('LOWER_TIMEFRAME_MIN')
        ltfmindelta = datetime.timedelta(minutes=ltfmin)
        tickinteval = 1
        symbol = 'SUNPHARMA'
        token = 857857
        for i, row in data.iterrows():
            ticks = [{'instrument_token': token, 'tradingsymbol': symbol,
                      'timestamp': i, 'last_price': row['Open']}]
            self.on_ticks(None, ticks)
            time.sleep(tickinteval)
            ifh = random.randint(0, 1)
            ticks = [{'instrument_token': token, 'tradingsymbol': symbol, 'timestamp': i + ltfmindelta /
                      4, 'last_price': row['High'] if ifh else row['Low']}]
            self.on_ticks(None, ticks)
            time.sleep(tickinteval)
            ticks = [{'instrument_token': token, 'tradingsymbol': symbol, 'timestamp': i + ltfmindelta /
                      2, 'last_price': row['Low'] if ifh else row['High']}]
            self.on_ticks(None, ticks)
            time.sleep(tickinteval)
            ticks = [{'instrument_token': token, 'tradingsymbol': symbol,
                      'timestamp': i+ltfmindelta, 'last_price': row['Close']}]
            self.on_ticks(None, ticks)
            time.sleep(tickinteval)
