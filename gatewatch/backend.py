import json

import redis


REDIS = redis.StrictRedis(host='localhost', port=6379, db=1)


def read(key, default=None):
    value = REDIS.get(key)
    if value is None:
        return default
    return json.loads(value)


def write(**kwargs):
    for key, value in kwargs.iteritems():
        REDIS.set(key, json.dumps(value))
