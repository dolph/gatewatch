import argparse
import datetime
import os

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
def get_gating_changes():
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
    top_change = get_gating_changes()[0]

    # calculate number of seconds since the change was enqueued
    enqueued_timestamp = top_change['enqueue_time'] / 1000.
    enqueued_dt = datetime.datetime.fromtimestamp(enqueued_timestamp)
    seconds = (datetime.datetime.now() - enqueued_dt).seconds

    # if the gate has an estimate for when all jobs are complete, add that
    if top_change['remaining_time'] is not None:
        seconds = seconds + top_change['remaining_time'] / 1000.

    return seconds


def human_readable_duration(seconds):
    """Converts an integer in seconds to a human readable string."""
    if seconds / 60 / 60 > 1:
        return '%d hours' % round(seconds / 60. / 60.)
    elif seconds / 60 > 1:
        return '%d minutes' % round(seconds / 60.)
    else:
        return '%d seconds' % round(seconds / 60.)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    print('Gate duration: %s' % human_readable_duration(get_gate_duration()))
