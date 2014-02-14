import argparse
import datetime
import os
import time

import dogpile.cache
import requests


CACHE_DIR = os.path.expanduser('~/.openstack-hud')
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR, 0o0700)

CACHE = dogpile.cache.make_region().configure(
    'dogpile.cache.dbm',
    expiration_time=15,
    arguments={'filename': '%s/cache.dbm' % CACHE_DIR})

PROJECT = 'openstack/keystone'


@CACHE.cache_on_arguments()
def get_zuul_status():
    r = requests.get('http://zuul.openstack.org/status.json')
    return r.json()


@CACHE.cache_on_arguments()
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
    top_change = list_gating_changes()[0]

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


def human_readable_duration(seconds):
    """Converts a large number of seconds to a human readable tuple.

    :returns: (int, "unit of time")

    """
    if seconds / 60. / 60. / 24. / 7. / 52. > 1:
        t = (seconds / 60. / 60. / 24. / 7. / 52., 'years')
    elif seconds / 60. / 60. / 24. / 7. / (52. / 12.) > 1:
        t = (seconds / 60. / 60. / 24. / 7. / (52. / 12.), 'months')
    elif seconds / 60. / 60. / 24. / 7. > 1:
        t = (seconds / 60. / 60. / 24. / 7., 'weeks')
    elif seconds / 60. / 60. / 24. > 1:
        t = (seconds / 60. / 60. / 24., 'days')
    elif seconds / 60. / 60. > 1:
        t = (seconds / 60. / 60., 'hours')
    elif seconds / 60. > 1:
        t = (seconds / 60., 'minutes')
    else:
        t = (seconds, 'seconds')

    # convert to an int
    value = int(round(t[0]))

    # drop plurality on the unit if appropriate
    units = t[1] if value != 1 else t[1][:-1]

    return (value, units)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    # should come from args
    projects = [
        PROJECT,
        'openstack/python-keystoneclient',
        'openstack/identity-api']

    print(
        'Gate duration: %d %s' % human_readable_duration(get_gate_duration()))

    print('Gating changes:')
    for change in list_gating_changes_to_projects(projects):
        value, units = human_readable_duration(change['eta'])
        print('  %s: %d %s' % (change['url'], value, units))
