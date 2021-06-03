from datetime import datetime
import os
import webbrowser
from kiteconnect import KiteConnect
from libs.configs import getConfig, setConfig


def get_access_token(kite):
    now = datetime.now()
    session = f'{now.year}{now.month:02}{now.day:02}'
    tokenfile = 'files/' + session + '.txt'
    if os.path.exists(tokenfile):
        print('Getting saved access token...')
        with open(tokenfile, 'r') as f:
            access_token = f.read()
            print('... done!')
            return access_token
    # webbrowser.open(kite.login_url(), new=0, autoraise=True)
    # session = input('Enter session name: ')
    print("Open")
    print(kite.login_url())
    webbrowser.open(kite.login_url(), new=0, autoraise=True)
    request_token = input('Enter request token: ')
    if (request_token == ''):
        exit()
    data = kite.generate_session(request_token, api_secret=getConfig('api_secret'))
    # kite.request_access_token(request_token, api_secret=config['api_secret'])
    access_token = data['access_token']
    with open(tokenfile, 'w') as f:
        print('saving access token...')
        f.write(access_token)
        print('... done!')
    return access_token

def run_access():
    kite = KiteConnect(api_key=getConfig('api_key'))
    access_token = get_access_token(kite)
    now = datetime.now()
    print()
    val = f'{now.year}{now.month:02}{now.day:02}:{access_token}'
    print('Run – ')
    print(f'export ACCESS_TOKEN={val}')
    # os.environ['ACCESS_TOKEN'] = val
    # CONFIGS['ACCESS_TOKEN'] = (val, str)
    setConfig('ACCESS_TOKEN', val)
    print()

if __name__ == "__main__":
    run_access()