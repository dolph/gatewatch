import datetime

import celery


BROKER_URL = 'redis://localhost:6379/0'


# start dedicated celery beat worker with:
# celery -A gatewatch.tasks worker --beat --loglevel=info
app = celery.Celery('tasks', broker=BROKER_URL)
app.conf.update(
    CELERY_TIMEZONE='UTC',
    CELERYBEAT_SCHEDULE={
        'gather-data-every-30-seconds': {
            'task': 'gatewatch.tasks.gather_data',
            'schedule': datetime.timedelta(seconds=30),
        },
    },
)


import redis


REDIS = redis.StrictRedis(host='localhost', port=6379, db=1)


def read(key, default=None):
    value = REDIS.get(key)
    if value is None:
        return default
    return value


def write(key, value):
    REDIS.set(key, value)


@app.task
def gather_data():
    write('test', 'success')
