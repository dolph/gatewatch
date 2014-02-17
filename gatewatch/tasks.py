import datetime

import celery

from gatewatch import backend


PROJECTS = ['openstack/keystone', 'openstack/python-keystoneclient']

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
        'get-gate-duration': {
            'task': 'gatewatch.zuul.get_gate_duration',
            'schedule': datetime.timedelta(minutes=1),
        },
        'get-gating-changes': {
            'task': 'gatewatch.zuul.list_gating_changes_to_projects',
            'schedule': datetime.timedelta(minutes=1),
            'arguments': (PROJECTS,),
        },
    },
)


@app.task
def gather_data():
    value = backend.read('incrementing', 0)
    backend.write(incrementing=value + 1)
