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


def time_ago(dt):
    delta = datetime.datetime.now() - dt
    if delta.seconds / 60 / 60 > 1:
        return '%d hours' % round(delta.seconds / 60. / 60.)
    elif delta.seconds / 60 > 1:
        return '%d minutes' % round(delta.seconds / 60.)
    else:
        return '%d seconds' % round(delta.seconds / 60.)


@CACHE.cache_on_arguments()
def get_gate_duration():
    top_change = get_gating_changes()[0]
    seconds = top_change['enqueue_time'] / 1000.
    dt = datetime.datetime.fromtimestamp(seconds)
    return time_ago(dt)


def list_gating_changes():
    top_change = get_gating_changes()[0]
    seconds = top_change['enqueue_time'] / 1000.
    dt = datetime.datetime.fromtimestamp(seconds)
    print('Gate duration: %s' % time_ago(dt))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    print('Gate duration: %s' % get_gate_duration())
