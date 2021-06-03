from libs.configs import getConfig
import datetime
from libs.values import holiday_dates
from libs.init_kite import KiteWrapper


kite = KiteWrapper().kite
def get_nifty_contracts():
    'trade for OTM strikes only [for now]'
    'To avoid issue with allowed strike price of the week, go for the next week contract'
    nifty = f'{kite.EXCHANGE_NSE}:NIFTY 50'
    nifty_price = round(kite.ltp(nifty)[nifty]['last_price'])
    today = datetime.datetime.today().date()
    weekday = today.weekday()
    thursday = 3
    isLastThursday = False
    if(weekday < thursday):
        expiry_date = today + datetime.timedelta(days=7+(thursday - weekday))
    else:
        expiry_date = today + datetime.timedelta(days=(7-(weekday-thursday)))

    cmonth = expiry_date.month
    nextExpiry = expiry_date + datetime.timedelta(days=7)
    isLastThursday = cmonth != nextExpiry.month

    if(expiry_date in holiday_dates):
        expiry_date = expiry_date - datetime.timedelta(days=1)
        cmonth = expiry_date.month
        nextExpiry = expiry_date + datetime.timedelta(days=8)
        isLastThursday = cmonth != nextExpiry.month

    niftyResolution = int(getConfig('nifty_strike_resolution'))
    dx = nifty_price % niftyResolution

    if(isLastThursday):
        inst_symbol = f'{kite.EXCHANGE_NFO}:NIFTY21{expiry_date.strftime("%B").upper()}'
    else:
        inst_symbol = f'{kite.EXCHANGE_NFO}:NIFTY21{expiry_date.month}{datetime.datetime.strftime(expiry_date, "%d")}'

    'For CE'
    currentstrike = nifty_price + niftyResolution - dx
    max_strike_price = int(getConfig('nifty_upper_strike'))
    inst_ce_options = []
    while(currentstrike <= max_strike_price):
        inst_ce_options.append(f'{inst_symbol}{currentstrike}CE')
        currentstrike += niftyResolution
    'For PE'
    currentstrike = nifty_price - dx
    min_strike_price = int(getConfig('nifty_lower_strike'))
    inst_pe_options = []
    while(currentstrike >= min_strike_price):
        inst_pe_options.append(f'{inst_symbol}{currentstrike}PE')
        currentstrike -= niftyResolution

    premiums = kite.ltp([inst for inst in [*inst_ce_options, *inst_pe_options]])
    # print(premiums)
    # import pdb; pdb.set_trace()
    ce_premiumns = [(k.split(':')[-1], premiums[k]['last_price']) for k in premiums.keys() if k in inst_ce_options]
    pe_premiumns = [(k.split(':')[-1], premiums[k]['last_price']) for k in premiums.keys() if k in inst_pe_options]
    return {'ce': ce_premiumns, 'pe': pe_premiumns}
