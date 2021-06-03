'Responsible for consistency of orders and updates'
from libs.values import PCONSTS
from libs.pubsub import get_ps_1
from kiteconnect import KiteConnect
from libs.init_kite import KiteWrapper
from libs.orderapi import Orderapi
from libs.values import PostEntryActions

r = get_ps_1()

orderapi = Orderapi()

kite = KiteWrapper().kite


def _update_positions():
    orders = kite.orders()
    positions = r.hgetall('positions')
    if(positions is None):
        print('No current positions')
        return
    netpositions = kite.positions()['net']
    for symbol in positions:
        'check current position'
        if(symbol in [x['tradingsymbol'] for x in netpositions if x['quantity'] != 0]):
            'what to update'
            '1. update status, '
            pos = positions[symbol]
            pos['updates']['status'] = KiteConnect.STATUS_COMPLETE
            'order_id should be there already'
            'counter_order_id may not be there due to interruption'
            orders1 = [order for order in orders if order['tradingsymbol'] ==
                       symbol and order['status'] not in [KiteConnect.STATUS_COMPLETE]]
            'The first order should contain parent order id if CO'
            if(len(orders1) > 0):
                pos['updates']['counter_order_id'] = orders1[0]['order_id']
            r.hset('positions', {symbol: pos})
            print('[POSITION]', symbol, pos['params']['transaction_type'],
                  pos['updates']['order_id'], pos['updates']['status'])

        else:
            'position squared'
            r.r.hdel('positions', symbol)


def update_positions():
    try:
        _update_positions()
    except Exception as ex:
        print('[ERROR]', ex.__str__())


def handler(channel, data):
    # print(channel, data)
    if(channel == 'connection'):
        if(data == 'connected'):
            update_positions()
    'TODO do this on candle updates, applicable for idx trades only.'
    # if(channel == PCONSTS.ticks.name):
    #     'exclude two legs orders, and position with existing counter_order_id, but idxstoploss given'
    #     ps = r.hgetall('positions')
    #     if(ps is None):
    #         # print('no positions')
    #         return
    #     ss = [s for s in ps if (ps[s].get('idxstoploss') != None) and (ps[s]['variety'] not in [
    #         KiteConnect.VARIETY_CO]) and (ps[s].get('counter_order_id') == None)]
    #     for s in ss:
    #         p = ps[s]
    #         sl = p['idxstoploss']
    #         idxsymbol = p['idxsymbol']
    #         lastprice = r.get(f'last_price-{idxsymbol}')
    #         if((p['transaction_type'] == KiteConnect.TRANSACTION_TYPE_BUY) and (lastprice <= sl) or (p['transaction_type'] == KiteConnect.TRANSACTION_TYPE_SELL) and (lastprice >= sl)):
    #             orderapi.exit_order(
    #                 instsymbol=p['tradingsymbol'], action=PostEntryActions.exit_all)

    if(channel == 'order_update'):
        # print(channel, data)
        'update position status'
        instsymbol = data['tradingsymbol']
        status = data['status']
        order_id = data['order_id']
        parent_order_id = data['parent_order_id']
        txntype = data['transaction_type']
        average_price = data['average_price']
        qty = data['quantity']
        stoploss = data['trigger_price']
        product = data['product']
        'This can be first leg or 2nd leg for co. or SL order'
        'if first leg order'
        position = r.hget('positions', instsymbol)
        print()
        print('[UPDATE]', instsymbol, *[data[x]
                                        for x in ['transaction_type', 'order_id', 'status']], product)
        if(position is None):
            'But this may have been placed manually or exited already.'
            print(
                'Error. Position empty but order update [may be manual] or exited already')
            return
        else:
            'order placed, '
            if(position['params']['transaction_type'] == txntype):
                print('entry ', instsymbol)
                if(status in [KiteConnect.STATUS_REJECTED, KiteConnect.STATUS_CANCELLED]):
                    print('order rejected. deleting position', instsymbol)
                    r.r.hdel('positions', instsymbol)     
                    return
                if(status == KiteConnect.STATUS_COMPLETE):
                    print('updating status')
                    position['updates']['order_id'] = order_id
                    position['updates']['status'] = status
                    position['params']['average_price'] = average_price
                    r.hset('positions', {instsymbol: position})
                    'for regular order, place the counter order'
                    if(position['params']['variety'] == KiteConnect.VARIETY_REGULAR):
                        if(position['updates'].get('stoploss') is not None):
                            orderapi._place_counter_mis_slorder(inst_symbol=instsymbol)
            else: 
                print('counter order', instsymbol)
                if(status == KiteConnect.STATUS_COMPLETE):
                    print('deleting completed', instsymbol)
                    r.r.hdel('positions', instsymbol)
                else:
                    if(status in [KiteConnect.STATUS_REJECTED, KiteConnect.STATUS_CANCELLED]):
                        orderapi.exit_order_m(instsymbol=instsymbol, action=PostEntryActions.exit_all)
                    else:
                        print('updating counter order', instsymbol, order_id)
                        position['updates']['counter_order_id'] = order_id
                        r.hset('positions', {instsymbol: position})

if(__name__ == '__main__'):
    update_positions()
    r.subscribe(['order_update', 'connection'], handler)
