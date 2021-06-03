
from libs.pubsub import get_ps_1, get_ps_2
from libs.instruments import get_instrument_tokens
from libs.values import PCONSTS
from libs.init_kite import KiteWrapper
'This is connection point to main server. and meant to run without interruptions and any complex calculations'
def connect():
    'This module is intended to run continuously. '

    proxy = input('Proxy: y/n: ')

    r = get_ps_1()

    # r.r.delete()
    
    r.set('is_proxy', proxy)
    kw = KiteWrapper()
    # kite = kw.kite

    kws = kw.kws

    def on_connect(ws, response):
        print('[CONNECTED]')
        tokens = get_instrument_tokens()
        kws.subscribe(tokens)
        kws.set_mode(kws.MODE_FULL, tokens)
        r.publish(PCONSTS.connection.name, PCONSTS.connected.name)


    def on_close(ws, code, reason):
        print('[CLOSED]')
        r.publish(PCONSTS.connection.name, PCONSTS.closed.name)

    def on_ticks(ws, ticks):
        r.publish(PCONSTS.ticks.name, ticks)

    def on_error(ws, code, reason):
        print('[ERROR]')
        r.publish(PCONSTS.connection.name, PCONSTS.error.name)

    def on_message(ws, payload, is_binary):
        pass

    def on_reconnect(ws, attempts_count):
        print('[RECONNECTING]')
        r.publish(PCONSTS.connection.name, PCONSTS.reconnecting.name)

    def on_noreconnect(ws):
        print('NO RECONNECTION')
        kws.close()

    def on_order_update(ws, data):
        # print('[ORDER UPDATE')
        r.publish(PCONSTS.order_update.name, data)
        

    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.on_ticks = on_ticks
    kws.on_error = on_error
    kws.on_message = on_message
    kws.on_reconnect = on_reconnect
    kws.on_noreconnect = on_noreconnect
    kws.on_order_update = on_order_update
    kws.connect()

if __name__ == "__main__":
    connect()