import datetime

import celery


PROJECTS = ['openstack/keystone', 'openstack/python-keystoneclient']
PRIMARY_PROJECT = PROJECTS[0]

BROKER_URL = 'redis://localhost:6379/0'

# start dedicated celery beat worker with:
# celery -A gatewatch.tasks worker --beat --loglevel=info
app = celery.Celery('tasks', broker=BROKER_URL)
app.conf.update(
    CELERY_TIMEZONE='UTC',
    CELERYBEAT_SCHEDULE={
        'count-open-reviews': {
            'task': 'gatewatch.sources.gerrit.count_open_reviews',
            'schedule': datetime.timedelta(minutes=1),
        },
        'count-failed-merges': {
            'task': 'gatewatch.sources.gerrit.count_failed_merges',
            'schedule': datetime.timedelta(minutes=1),
        },
        'get-gate-duration': {
            'task': 'gatewatch.sources.zuul.get_gate_duration',
            'schedule': datetime.timedelta(minutes=1),
        },
        'get-gating-changes': {
            'task': 'gatewatch.sources.zuul.list_gating_changes_to_projects',
            'schedule': datetime.timedelta(minutes=1),
            'args': (PROJECTS,),
        },
        'next-milestone-date': {
            'task': 'gatewatch.sources.launchpad.next_milestone_date',
            'schedule': datetime.timedelta(seconds=1),
            'args': (PRIMARY_PROJECT,),
        },
    },
    CELERY_IMPORTS=('gatewatch.sources'),
)