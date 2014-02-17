import datetime
import time

import requests

from gatewatch import cache


PROJECT = 'openstack/keystone'


@cache.cache_on_arguments()
def get_zuul_status():
    r = requests.get('http://zuul.openstack.org/status.json')
    return r.json()


@cache.cache_on_arguments()
def list_gating_changes():
    status = get_zuul_status()
    gate = [x for x in status['pipelines'] if x['name'] == 'gate'].pop()
    queue = [x for x in gate['change_queues'] if PROJECT in x['name']].pop()

    changes = []
    for head in queue['heads']:
        for change in head:
            changes.append(change)
    return changes


def get_gate_duration():
    """Returns the number of seconds required to land a change."""
    # look at the top change in the queue
    changes = list_gating_changes()
    if not changes:
        return 0
    top_change = changes[0]

    # calculate number of seconds since the change was enqueued
    enqueued_timestamp = top_change['enqueue_time'] / 1000.
    enqueued_dt = datetime.datetime.fromtimestamp(enqueued_timestamp)
    seconds = (datetime.datetime.now() - enqueued_dt).seconds

    # if the gate has an estimate for when all jobs are complete, add that
    if top_change['remaining_time'] is not None:
        seconds = seconds + top_change['remaining_time'] / 1000.

    return seconds


def list_gating_changes_to_projects(projects):
    """Returns the number of seconds required to land a change."""
    gate_duration = get_gate_duration()
    now = time.time()

    changes = []
    for change in list_gating_changes():
        # skip changes to other projects
        if change['project'] not in projects:
            continue

        # calculate the estimated time until a patch is merged
        eta = int(round(change['enqueue_time'] / 1000. + gate_duration - now))
        changes.append(dict(
            url=change['url'],
            eta=eta))

    return changes
