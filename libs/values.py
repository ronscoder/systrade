from enum import Enum
from collections import namedtuple
from typing import NamedTuple
from kiteconnect import KiteConnect
import datetime

'NOTE: Always use the same variable name and Enum classname'

PCONSTS = Enum('PCONSTS', 'connection connected closed error reconnecting ticks order_update')

PostEntryActions = Enum('PostEntryActions', 'exit_all exit_partial update_qty update_sl')

# class PostEntryActions(Enum):
#     exit_all = 1
#     exit_partial = 2
#     update_qty = 3
#     update_sl = 4


PostEntryActions.exit_all

class EntrySignal(NamedTuple):
    idxsymbol:str
    stoploss: float
    direction: int
    entrymethod: str
    entrycode: str

class PostEntrySignal(NamedTuple):
    idxsymbol: str
    action: PostEntryActions


holidays = ['2021-01-26',
            '2021-03-11',
            '2021-03-29',
            '2021-04-02',
            '2021-04-14',
            '2021-04-21',
            '2021-05-13',
            '2021-07-21',
            '2021-08-19',
            '2021-09-10',
            '2021-10-15',
            '2021-11-04',
            '2021-11-05',
            '2021-11-19']

holiday_dates = [datetime.datetime.strptime(x, '%Y-%m-%d').date() for x in holidays]            

weekdays = {'monday': 0}

def isNonTradingDay(d: datetime):
        return (d in holiday_dates) or (d.weekday() in [5, 6])