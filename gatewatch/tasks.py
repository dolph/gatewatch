import datetime

import celery

from gatewatch import backend


BROKER_URL = 'redis://localhost:6379/0'


# start dedicated celery beat worker with:
# celery -A gatewatch.tasks worker --beat --loglevel=info
app = celery.Celery('tasks', broker=BROKER_URL)
app.conf.update(
    CELERY_TIMEZONE='UTC',
    CELERYBEAT_SCHEDULE={
        'gather-data-every-30-seconds': {
            'task': 'gatewatch.tasks.gather_data',
            'schedule': datetime.timedelta(seconds=3),
        },
    },
)


@app.task
def gather_data():
    value = backend.read('incrementing', 0)
    backend.write(incrementing=value + 1)
