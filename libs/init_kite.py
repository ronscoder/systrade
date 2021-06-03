from kiteconnect import KiteConnect, KiteTicker
import os
import datetime
from libs.configs import getConfig
from libs.access import run_access
from libs.kite_fake import ProxyKiteConnect, ProxyKiteTicker
from libs.pubsub import get_ps_1


class KiteWrapper:
    def __init__(self) -> None:
        self.r = get_ps_1()
        if(not(self.r.get('is_proxy') == 'y')):
            self.kite,self.kws = self.getKite()
        else:
            self.kite = ProxyKiteConnect()
            self.kws = ProxyKiteTicker()

    def getKite(self):
            run_access()
            access_token = getConfig('ACCESS_TOKEN')
            if(access_token is None):
                raise Exception('Acess token not set')
            tokendatestr, self.token = access_token.split(":")
            tokendate = datetime.date(int(tokendatestr[:4]), int(
                tokendatestr[4:6]), int(tokendatestr[6:8]))
            today = datetime.date.today()
            if(today != tokendate):
                raise Exception('Token date expired')
            kite = KiteConnect(api_key=getConfig(
                'api_key'), access_token=self.token)
            kws = KiteTicker(getConfig('api_key'), self.token)
            return kite, kws
