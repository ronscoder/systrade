'This is where the calculations are done'
from libs.pubsub import get_ps_1
from libs.instruments import get_instruments
# from libs.calculation import Calculation
from libs.calculationfft import Calculation

r = get_ps_1()


def handler(channel, data):
    tftype = data['tftype']
    symbol = data['symbol']
    print(symbol, tftype)
    if(tftype in calcs[symbol]):
        calcs[symbol][tftype].on_data(data)
    # print(f'{symbol} SR[{tftype}][{calcs[symbol][tftype].shistory[-1]},{calcs[symbol][tftype].rhistory[-1]}]')
    r.publish(f'CALC-{symbol}-{tftype}', {'symbol': symbol,
                                        'tftype': tftype, 'calc': calcs[symbol]})

insts = get_instruments()

calcs = {x['symbol']: {'LTF': Calculation()}
         for x in insts}
         
for s in calcs:
    calcs[s]['LTF'].calc()


if(__name__ == '__main__'):
    print('waiting for ohlc updates')
    r.subscribe([f'INSTRUMENT-{x["symbol"]}-OHLC-*' for x in insts], handler)
    'TODO: add restart channel'
