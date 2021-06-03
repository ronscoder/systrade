import redis
import pickle

def get_ps_1():
    'For dynamic/runtime data'
    return PubSub(db=1)

def get_ps_2():
    'For persisting data'
    return PubSub(db=2)

class PubSub:
    def __init__(self, db=0) -> None:
        self.r = redis.Redis(db=db)
        self.ps = self.r.pubsub()

    def set(self, key, data):
        msg = pickle.dumps(data)
        self.r.set(key, msg)
    
    def get(self, key):
        msg = self.r.get(key)
        if(msg):
            data = pickle.loads(msg)
            return data

    def _set(self, key, msg):
        self.r.set(key, msg)
    
    def _get(self, key):
        msg = self.r.get(key)
        if(msg):
            return msg.decode('utf-8')
    
    def decode(self,data):
        return data.decode('utf-8')

    def hset(self, key, mapping):
        self.r.hset(key, mapping={k: pickle.dumps(mapping[k]) for k in mapping})

    def lpush(self, key, value):
        self.r.lpush(key, pickle.dumps(value))
    
    def lrange(self,key):
        return pickle.loads(self.r.lrange(key, 0, -1))

    def hget(self, key, field):
        data = self.r.hget(key, field)
        if(data):
            return pickle.loads(data)

    def hgetall(self, key):
        data = self.r.hgetall(key)
        if(data):
            return {k.decode('utf-8'): pickle.loads(data[k]) for k in data}

    def publish(self, channel, data):
        self.set(channel, data)
        msg = pickle.dumps(data)
        self.r.publish(channel, msg)

    def subscribe(self, channels, cb):
        self.ps.psubscribe(channels)
        for msg in self.ps.listen():
            typ = msg['type']
            if(typ=='psubscribe'):
                continue
            channel = msg['channel'].decode('utf-8')
            data = msg['data']
            dataobj = pickle.loads(data)            
            cb(channel, dataobj)
