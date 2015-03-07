# 
# Realtime Analytics Using MongoDB, Python, Gevent, and ZeroMQ
# http://www.slideshare.net/rick446/realtime-analytics-using-mongodb-python-gevent-and-zeromq



class IdGen(object):
    '''
    Autoincrement integers are harder
    than in MySQL but not impossible
    '''
    @classmethod
    def get_ids(cls, inc=1):
        obj = cls.query.find_and_modify(
                    query={'_id' : 0},
                    update={
                        '$inc' : dict(inc=inc),
                        },
                    upsert=True,
                    new=True)
        return range(obj.inc - inc, obj.inc)

        
