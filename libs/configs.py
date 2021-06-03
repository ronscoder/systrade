from math import floor
import os
from libs.pubsub import get_ps_2

rconfig = get_ps_2()
"""
Only for defaultable parameters
"""
# CONFIGS = dict(TRAILING_SL_ABOVE_ENTRY=(0.01, float), TRAIL_GAP=(0.002, float),
#            STOP_LOSS=(0.02, float),
#            MAX_NO_POSITION=(5, int),
#            FUND_TO_RESERVE=(2000, float),
#            CANDLE_PERIODS_SECS=('300,900', str),
#            MARKET_DIRECTION=(1, int),  # 1=Bullish, -1=Bearish, 0=BOTH
#            HALT=(0, int),
#            SQOFF_CO_MIN=(10, int),  # last minute to start square off 2nd leg
#            STOP_ENTRY = (0, int),
#            EXIT_THRESHOLD = (1.5, float),
#            MANUAL_BUT_TRAIL = (1, bool),
#            FNO_P1 = (0.15, float),
#            FNO_P2 = (0.075, float)
#            )
# CONFIGS = {
#     'HALT': (0, int),
#     'LOWER_TIMEFRAME_MIN': (5, float),
#     'MULTI_TF_FACTOR': (3, int),
#     'HTF_HISTORY_PERIOD_DAYS': (2, int),
#     'LTF_HISTORY_PERIOD_DAYS': (1, int),
#     'HIST_RECALC_LENGTH': (27, int),
#     'HTF_RECALC_PERIOD': (2, int),
#     'HTF_HIST_RECALC_SKIP_LAST': (1, int),
#     'LTF_RECALC_PERIOD': (3, int),
#     'LTF_HIST_RECALC_SKIP_LAST': (2, int),
#     'DACC_MOMENTUM_FACTOR': (0.1, float),
#     'MOMENTUM_PERIOD': (4, int),
#     'api_key': ('7zx0e8g535qgefu6', str),
#     'api_secret': ('utwyn9ugmbxfcx6wurcd869mtvn2ck30', str),
#     'user_id': ('YZ7009', str),
#     'backtest':(False, bool),
#     'ACCURACY':(4,int),
#     'MIN_RANGE_GAP': (0.001, float),
#     'DAY_FUND': (200, float), #TODO precheck if this margin is met
#     'ALLOCATION_RATIO': (2, int),
#     'max_strike_price': (15200, float),
#     'min_strike_price': (14000, float),
#     'log_level': (2, int), #1: any info, 2: , 3:
#     'save_snapshots': (1, int)
# }
_CONFIGS = {
    'HALT': (0, int),
    'LOWER_TIMEFRAME_MIN': (5, float),
    'MULTI_TF_FACTOR': (3, int),
    'HTF_HISTORY_PERIOD_DAYS': (2, int),
    'LTF_HISTORY_PERIOD_DAYS': (1, int),
    'HIST_RECALC_LENGTH': (27, int),
    'HTF_RECALC_PERIOD': (2, int),
    'HTF_HIST_RECALC_SKIP_LAST': (0, int),
    'LTF_RECALC_PERIOD': (3, int),
    'LTF_HIST_RECALC_SKIP_LAST': (3, int),
    'DACC_MOMENTUM_FACTOR': (0.1, float),
    'MOMENTUM_PERIOD': (4, int),
    'GOOD_PC': (0.45/100, float),
    'api_key': ('7zx0e8g535qgefu6', str),
    'api_secret': ('utwyn9ugmbxfcx6wurcd869mtvn2ck30', str),
    'user_id': ('YZ7009', str),
    'backtest': (False, bool),
    'ACCURACY': (4, int),
    'MIN_RANGE_GAP': (0.001, float),
    'DAY_FUND': (1000, float),  # TODO precheck if this margin is met
    'ALLOCATION_RATIO': (2, int),  # TODO check no of positions
    'nifty_upper_strike': (15800, int),  # Allowed upper strike
    'nifty_lower_strike': (14600, int),  # ALlowed lower strike
    # 500 points below and above the current point
    'nifty_strike_resolution': (50, int),
    'log_level': (0, int),  # 1: any info, 2: , 3:
    'save_snapshots': (0, int)
}
CONFIGS = {
    'HALT': 0,
    'LOWER_TIMEFRAME_MIN': 5,
    'MULTI_TF_FACTOR': 3,
    'HTF_HISTORY_PERIOD_DAYS': 2,
    'LTF_HISTORY_PERIOD_DAYS': 1,
    'HIST_RECALC_LENGTH': 27,
    'HTF_RECALC_PERIOD': 2,
    'HTF_HIST_RECALC_SKIP_LAST': 0,
    'LTF_RECALC_PERIOD': 3,
    'LTF_HIST_RECALC_SKIP_LAST': 3,
    'DACC_MOMENTUM_FACTOR': 0.1,
    'MOMENTUM_PERIOD': 4,
    'GOOD_PC': 0.45/100,
    'api_key': '7zx0e8g535qgefu6',
    'api_secret': 'utwyn9ugmbxfcx6wurcd869mtvn2ck30',
    'user_id': 'YZ7009',
    'backtest': False,
    'ACCURACY': 2,
    'MIN_RANGE_GAP': 0.001,
    'DAY_FUND': 1000,   # TODO precheck if this margin is met
    'ALLOCATION_RATIO': 2,   # TODO check no of positions
    'nifty_upper_strike': 15800,   # Allowed upper strike
    'nifty_lower_strike': 14600,   # ALlowed lower strike
    # 500 points below and above the current point
    'nifty_strike_resolution': 50,
    'log_level': 0,   # 1: any info, 2: , 3:
    'save_snapshots': 0,
    'maxn_points': 90,
}



def getConfig(varname):
    'Try to fetch data from redis first'
    data = rconfig.hget('configs', varname)
    if(data is None):
        data = CONFIGS[varname]
    return data

def setConfig(varname, val):
    rconfig.hset('configs', {varname:val})
    rconfig.r.save()

def setInitial():
    rconfig.hset('configs', CONFIGS)
    rconfig.r.save()

def _getConfig(varname):
    'Try to fetch data from redis first'
    var = os.environ.get(varname)
    if(var is None):
        data = CONFIGS[varname][0]
    else:
        data = CONFIGS[varname][1](var)
    return data
