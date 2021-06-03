from libs.pubsub import get_ps_1
import matplotlib.pyplot as plt
from custom_package import candle
from libs.instruments import get_instruments
# from libs.calculation import Calculation
from libs.calculationfft import Calculation

r = get_ps_1()

insts = get_instruments()
'TODO: multiple charts for each instruments'
insts = [{'symbol': 'SUNPHARMA'}]
tfs = [5, 15]

# ohlc_channels = [f'OHLC-{x["symbol"]}-{tf}' for tf in tfs
#                  for x in insts]

'TODO: need to change'
sunpharma_ohlc_channel = 'INSTRUMENT-SUNPHARMA-OHLC-LTF'
sunpharma_calc_channel = 'CALC-SUNPHARMA-LTF'
plt.ion()
plt.suptitle(sunpharma_ohlc_channel)
plt.show(block=False)
ax1 = plt.subplot(2, 1, 1)
ax2 = plt.subplot(2, 1, 2)
'TODO register datetime converter explicitly'
'TODO plot the initial data (set initial data from instruments)'


class Monitor:
    def __init__(self) -> None:
        self.ohlc_ltf = None
        self.ohlc_htf = None
        self.sups = None
        self.ress = None
        self.shistory = []
        self.rhistory = []
        self.psup = None
        self.pres = None

    def on_data(self, channel, data):
        if(channel == sunpharma_ohlc_channel):
            if(data['tftype'] == 'HTF'):
                self.ohlc_htf = data['ohlcs']
            if(data['tftype'] == 'LTF'):
                self.ohlc_ltf = data['ohlcs']
        if(channel == sunpharma_calc_channel):
            if(data['tftype'] == 'LTF'):
                # print(data.keys())
                # print('history', len(self.shistory), len(self.rhistory))
                calc: Calculation = data['calc']['LTF']
                self.shistory = calc.shistory
                self.rhistory = calc.rhistory
                # (self.shistory, self.rhistory) = data['srhistory']
                self.psup, self.pres = calc.psup, calc.pres

        self.plot()

    def plot(self):
        plt.cla()
        if(self.ohlc_htf is not None):
            candle.timeplot(ax1, self.ohlc_htf)
        if(self.ohlc_ltf is not None):            
            candle.timeplot(ax2, self.ohlc_ltf)
        xsup = [x[0] for x in self.shistory]
        sups = [x[1] for x in self.shistory]
        ax2.plot(xsup, sups, color='#0000ff', linestyle='--', linewidth=1)
        xres = [x[0] for x in self.rhistory]
        ress = [x[1] for x in self.rhistory]
        ax2.plot(xres, ress, color='#ff0000', linestyle='--', linewidth=1)
        if(self.psup and self.ohlc_ltf is not None):            
            csups = [self.psup(x+1) for x in range(-len(self.ohlc_ltf), 0)]
            print('sr check')
            print(self.shistory[-2:])
            print(self.ohlc_ltf.index[-2:], csups[-2:])
            ax2.plot(self.ohlc_ltf.index, csups, color='#00ff00')
        if(self.pres and self.ohlc_ltf is not None):
            cress = [self.pres(x+1) for x in range(-len(self.ohlc_ltf), 0)]
            ax2.plot(self.ohlc_ltf.index, cress, color='#9d0000')
        plt.gcf().canvas.draw_idle()
        plt.gcf().canvas.start_event_loop(0.001)


if(__name__ == '__main__'):
    m = Monitor()
    'sunpharma_ohlc_channel data will be in sunpharma_calc_channel also'
    r.subscribe([sunpharma_ohlc_channel, sunpharma_calc_channel], m.on_data)
    print('done')
