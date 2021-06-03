import matplotlib.pyplot as plt
import pandas as pd
import datetime

def plot(ax, ohlcs, indices=None, is_df=False, alpha=0.5):
    if(is_df):
        ohlcs = ohlcs.to_dict('records')
    if(indices == None):
        indices = [i for i in range(len(ohlcs))]
    for x in indices:
        ohlc = ohlcs[x-indices[0]]
        ax.plot([x, x], [ohlc['High'], ohlc['Low']],
                color='black', linewidth=1, alpha=alpha)

        color = 'green' if ohlc['Open'] < ohlc['Close'] else 'red'

        if(abs(ohlc['Open'] - ohlc['Close']) < 0.01*abs(ohlc['High'] - ohlc['Low'])):
            ax.plot(x, ohlc['Close'], marker='_', color=color, alpha=alpha)
        else:
            ax.plot([x, x], [ohlc[y]
                             for y in ['Open', 'Close']], color=color, linewidth=4, alpha=alpha)
    # return ax
def timeplot(ax: plt.Axes, ohlcs: pd.DataFrame, alpha=0.5):
    for i, x in ohlcs.iterrows():
        ohlc = x
        ax.plot([i, i], [ohlc['High'], ohlc['Low']],
                color='black', linewidth=1, alpha=alpha)

        color = 'green' if ohlc['Open'] < ohlc['Close'] else 'red'

        if(abs(ohlc['Open'] - ohlc['Close']) < 0.01*abs(ohlc['High'] - ohlc['Low'])):
            ax.plot(i, ohlc['Close'], marker='_', color=color, alpha=alpha)
        else:
            ax.plot([i, i], [ohlc[y]
                             for y in ['Open', 'Close']], color=color, linewidth=4, alpha=alpha)
    # plt.xticks(ohlcs.index, labels=[datetime.datetime.strftime(x, "%H:%M") for x in ohlcs.index], rotation='vertical')
    plt.xticks(rotation='vertical')
    # plt.xticks(ohlcs.index, labels=[datetime.datetime.strftime(x, "%H:%M") for x in ohlcs.index])
    # plt.xticks(ohlcs.index, labels=[x.time() for x in ohlcs.index], rotation='vertical')
    

    # ax.set_xticks()
