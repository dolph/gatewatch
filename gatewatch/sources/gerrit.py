# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import getpass
import json
import socket
import time

import paramiko

from gatewatch import app
from gatewatch import backend
from gatewatch import cache
from gatewatch import tasks


# used for tracking the last known state of each change
COMMENTS = {}
STATUS = {}

CLIENT = None
CLIENT_KWARGS = dict()


def get_client(**kwargs):
    global CLIENT

    # remember client configuration
    CLIENT_KWARGS.update(kwargs)
    CLIENT_KWARGS.setdefault('host', app.config.get('GERRIT_HOST'))
    CLIENT_KWARGS.setdefault('port', app.config.get('GERRIT_PORT'))
    CLIENT_KWARGS.setdefault('user', app.config.get('GERRIT_USERNAME'))
    CLIENT_KWARGS.setdefault('key', app.config.get('GERRIT_KEY'))

    def ssh_client(host, port, user=None, key=None):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        try:
            client.connect(host, port=port, key_filename=key, username=user)
        except paramiko.PasswordRequiredException:
            password = getpass.getpass('SSH Key Passphrase: ')
            client.connect(
                host, port=port, key_filename=key, username=user,
                password=password)
        return client

    if CLIENT is None:
        # generate a new client
        app.logger.info('Creating gerrit client using: %s', CLIENT_KWARGS)
        CLIENT = ssh_client(**CLIENT_KWARGS)

    return CLIENT


def ssh_client_command(command):
    global CLIENT

    try:
        stdin, stdout, stderr = get_client().exec_command(command)
    except socket.error:
        # throw the client away, we'll build a new one next time
        CLIENT = None

        # retry
        stdin, stdout, stderr = get_client().exec_command(command)

    return stdin, stdout, stderr


@cache.cache_on_arguments(expiration_time=60 * 5)
def query(q):
    reviews = []

    limit = 100

    while True:
        query = [
            'gerrit', 'query', q, 'limit:%s' % limit, '--format=JSON']
        if reviews:
            query.append('resume_sortkey:%s' % reviews[-2]['sortKey'])
        try:
            stdin, stdout, stderr = ssh_client_command(' '.join(query))
        except paramiko.SSHException as e:
            app.logger.warning('Unable to query gerrit: %s' % e)
            return []

        for line in stdout:
            reviews.append(json.loads(line))
        if not reviews:
            raise Exception(stderr.read())
        if reviews[-1]['rowCount'] != limit:
            break

    return [x for x in reviews if 'id' in x]


def get_review(review_number):
    reviews = query(review_number)
    if reviews:
        return reviews.pop()


@tasks.app.task
def count_open_reviews():
    q = [
        'status:open',
        'AND (',
        'project:openstack/keystone',
        'OR project:openstack/python-keystoneclient',
        'OR project:openstack/identity-api',
        ')',
        'AND verified+1',
        'AND (-codereview-1)',
        'AND (-codereview-2)',
        'AND (-approved+1)']
    count = len(query(' '.join(q)))
    backend.write(open_reviews=count)
    return count


@tasks.app.task
def count_failed_merges():
    q = [
        'status:open',
        'AND (',
        'project:openstack/keystone',
        'OR project:openstack/python-keystoneclient',
        'OR project:openstack/identity-api',
        ')',
        'AND (verified-1 OR verified-2)',
        'AND codereview+2',
        'AND approved+1']
    count = len(query(' '.join(q)))
    backend.write(failed_merges=count)
    return count


@tasks.app.task
def recently_merged():
    q = [
        'status:merged',
        'AND (',
        'project:openstack/keystone',
        'OR project:openstack/python-keystoneclient',
        'OR project:openstack/identity-api',
        ')']
    reviews = query(' '.join(q))

    # including 'status:merged' with a negative 'age' seems to cause gerrit to
    # hang forever, so we need to do one or the other offline
    yesterday = time.time() - 60 * 60 * 24
    reviews = [x for x in reviews if x['lastUpdated'] > yesterday]

    reviews = reversed(reviews)
    backend.write(recently_merged=reviews)
    return reviews
