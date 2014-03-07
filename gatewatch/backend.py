import json

import redis

from gatewatch import app


REDIS = redis.StrictRedis(
    host=app.config['REDIS_HOST'],
    port=app.config['REDIS_PORT'],
    db=app.config['REDIS_DB'])


def read(key, default=None):
    value = REDIS.get(key)
    if value is None:
        return default
    return json.loads(value) if value is not None else default


def write(**kwargs):
    for key, value in kwargs.iteritems():
        REDIS.set(key, json.dumps(value))
