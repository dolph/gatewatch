import datetime
import json
import os

import flask

from gatewatch import app  # noqa
from gatewatch import backend
from gatewatch import decorators
from gatewatch.sources import gerrit
from gatewatch import utils


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


@app.route('/', methods=['GET'])
@decorators.templated()
def index():
    changes = backend.read('gating_changes', default=[])
    for change in changes:
        change['eta'] = utils.human_readable_duration(change['eta'])
        change['number'] = change['url'].split('/')[-1]

        review = gerrit.get_review(change['number'])
        change['subject'] = review['subject']

    return dict(changes=changes)


@app.route('/data', methods=['GET'])
def data():
    gate_duration = backend.read('gate_duration', default=0)

    next_milestone_date = backend.read('next_milestone_date', default=0)
    next_milestone_date = datetime.datetime.strptime(
        next_milestone_date, DATETIME_FORMAT)
    next_milestone = next_milestone_date - datetime.datetime.utcnow()
    next_milestone = next_milestone.days * 86400 + next_milestone.seconds

    changes = backend.read('gating_changes', default=[])
    for change in changes:
        change['eta'] = utils.human_readable_duration(change['eta'])
        change['number'] = change['url'].split('/')[-1]

        review = gerrit.get_review(change['number'])
        change['subject'] = review['subject']

    bp_percent = backend.read('blueprint_completion_percentage', default=41)

    d = dict(
        open_reviews=backend.read('open_reviews', default=0),
        gate_duration=utils.human_readable_duration(gate_duration),
        failed_merges=backend.read('failed_merges', default=0),
        next_milestone=utils.human_readable_duration(next_milestone),
        known_vulnerabilities=backend.read('known_vulnerabilities', default=0),
        blueprint_completion_percentage=bp_percent,
        changes=changes)

    return json.dumps(d), 200, {'Content-Type': 'application/json'}


@app.errorhandler(404)
def handle_not_found(error):
    return flask.render_template('not_found.html'), 404


@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/x-icon')
