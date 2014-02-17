import os

import flask

from gatewatch import app  # flake8: noqa
from gatewatch import backend
from gatewatch import collect
from gatewatch import decorators
from gatewatch import gerrit
from gatewatch import tasks


# should come from config
PROJECTS = [
    'openstack/keystone',
    'openstack/python-keystoneclient']


@app.route('/', methods=['GET'])
@decorators.templated()
def index():
    gate_duration = collect.get_gate_duration()

    changes = collect.list_gating_changes_to_projects(PROJECTS)
    for change in changes:
        change['eta'] = collect.human_readable_duration(change['eta'])
        change['number'] = change['url'].split('/')[-1]

        review = gerrit.get_review(change['number'])
        change['subject'] = review['subject']

    return dict(
        data=backend.read('incrementing', default=0),
        gate_duration=collect.human_readable_duration(gate_duration),
        changes=changes)


@app.errorhandler(404)
def handle_not_found(error):
    return flask.render_template('not_found.html'), 404


@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/x-icon')
