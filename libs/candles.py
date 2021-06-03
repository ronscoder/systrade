
class CandleUtility:
    def __init__(self, ohlcs) -> None:
        self.ohlcs = ohlcs
        self.fns = [self.engulfing, self.price_rejection, self.reverse_move]

    def isBull(self):
        return any([x() == 1 for x in self.fns])

    def isBear(self):
        return any([x() == -1 for x in self.fns])

    def engulfing(self):
        if(len(self.ohlcs) < 2):
            return
        ohlc0 = self.ohlcs.iloc[-1]
        ohlc1 = self.ohlcs.iloc[-2]

        bullEngulf = all([ohlc0['Open'] < x for x in [ohlc1[y]
                                                      for y in ['Open', 'Close']]]) \
            and all([ohlc0['Close'] > x for x in [ohlc1[y]
                                                  for y in ['Open', 'Close']]])
        if(bullEngulf):
            return 1

        bearEngulf = all([ohlc0['Open'] > x for x in [ohlc1[y]
                                                      for y in ['Open', 'Close']]]) \
            and all([ohlc0['Close'] < x for x in [ohlc1[y]
                                                  for y in ['Open', 'Close']]])
        if(bearEngulf):
            return -1

    def price_rejection(self):
        ''

    def reverse_move(self):
        if(len(self.ohlcs) < 3):
            return
        ltp = self.ohlcs.iloc[-1]['Close']
        o1 = self.ohlcs.iloc[-2]['Open']
        if(ltp > max(self.ohlcs.iloc[-3:-1]['Close']) and ltp > o1):
            return 1

        if(ltp < min(self.ohlcs.iloc[-3:-1]['Close']) and ltp < o1):
            return -1

    def is_price_weak(self, direction: int):
        if(len(self.ohlcs) < 2):
            return
        ltp = self.ohlcs.iloc[-1]['Close']
        o1 = self.ohlcs.iloc[-2]['Open']
        if(direction == 1):
            if(ltp < o1):
                return True
        if(direction == -1):
            if(ltp > o1):
                return True
        return False


