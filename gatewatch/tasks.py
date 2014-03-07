import datetime

import celery

from gatewatch import app

PROJECTS = ['openstack/keystone', 'openstack/python-keystoneclient']
PRIMARY_PROJECT = PROJECTS[0]

# start dedicated celery beat worker with:
# celery -A gatewatch.tasks worker --beat --loglevel=info
app = celery.Celery('tasks', broker=app.config['BROKER_URL'])
app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_TIMEZONE='UTC',
    CELERYBEAT_SCHEDULE={
        'count-open-reviews': {
            'task': 'gatewatch.sources.gerrit.count_open_reviews',
            'schedule': datetime.timedelta(minutes=5),
        },
        'count-failed-merges': {
            'task': 'gatewatch.sources.gerrit.count_failed_merges',
            'schedule': datetime.timedelta(minutes=15),
        },
        'get-gate-duration': {
            'task': 'gatewatch.sources.zuul.get_gate_duration',
            'schedule': datetime.timedelta(minutes=5),
        },
        'get-gating-changes': {
            'task': 'gatewatch.sources.zuul.list_gating_changes_to_projects',
            'schedule': datetime.timedelta(minutes=3),
            'args': (PROJECTS,),
        },
        'next-milestone-date': {
            'task': 'gatewatch.sources.launchpad.next_milestone_date',
            'schedule': datetime.timedelta(hours=6),
            'args': (PRIMARY_PROJECT,),
        },
    },
    CELERY_IMPORTS=('gatewatch.sources'),
)
