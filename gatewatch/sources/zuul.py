import datetime
import time

import requests

from gatewatch import backend
from gatewatch import cache
from gatewatch import tasks


PROJECT = 'openstack/keystone'


@cache.cache_on_arguments()
def get_zuul_status():
    r = requests.get('http://zuul.openstack.org/status.json')
    return r.json()


def _list_changes(pipeline_name):
    status = get_zuul_status()
    pipe = [x for x in status['pipelines'] if x['name'] == pipeline_name].pop()
    queue = [x for x in pipe['change_queues'] if PROJECT in x['name']].pop()

    changes = []
    for head in queue['heads']:
        for change in head:
            changes.append(change)
    return changes


@cache.cache_on_arguments()
def list_gating_changes():
    return _list_changes('gate')


@cache.cache_on_arguments()
def list_checking_changes():
    return _list_changes('check')


@tasks.app.task
def get_gate_duration():
    """Returns the number of seconds required to land a change."""
    # look at the top change in the queue
    changes = list_gating_changes()
    if not changes:
        return 0

    durations = []
    for change in changes:
        # calculate number of seconds since the change was enqueued
        enqueued_timestamp = change['enqueue_time'] / 1000.
        enqueued_dt = datetime.datetime.fromtimestamp(enqueued_timestamp)
        seconds = (datetime.datetime.now() - enqueued_dt).seconds

        # if the gate has an estimate for when all jobs are complete, add that
        if change['remaining_time'] is not None:
            seconds = seconds + change['remaining_time'] / 1000.

        durations.append(seconds)

    seconds = max(durations)

    backend.write(gate_duration=seconds)

    return seconds


def _list_changes_to_projects(projects, queued_changes):
    gate_duration = get_gate_duration()
    now = time.time()

    changes = []
    for change in queued_changes:
        # skip changes to other projects
        if change['project'] not in projects:
            continue

        # calculate the estimated time until a patch is merged
        eta = int(round(change['enqueue_time'] / 1000. + gate_duration - now))
        eta = eta if eta > 0 else 0
        changes.append(dict(
            url=change['url'],
            eta=eta))

    return changes


@tasks.app.task
def list_gating_changes_to_projects(projects):
    """Returns the number of seconds required to land a change."""
    changes = _list_changes_to_projects(projects, list_gating_changes())
    backend.write(gating_changes=changes)
    return changes


@tasks.app.task
def list_checking_changes_to_projects(projects):
    """Returns the number of seconds required to approve a change."""
    changes = _list_changes_to_projects(projects, list_checking_changes())
    backend.write(checking_changes=changes)
    return changes
