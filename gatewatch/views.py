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
    pass


@app.route('/data', methods=['GET'])
def data():
    gate_duration = backend.read('gate_duration', default=0)

    next_milestone_date = backend.read('next_milestone_date')
    if next_milestone_date is not None:
        next_milestone_date = datetime.datetime.strptime(
            next_milestone_date, DATETIME_FORMAT)
        next_milestone = next_milestone_date - datetime.datetime.utcnow()
        next_milestone = next_milestone.days * 86400 + next_milestone.seconds
    else:
        next_milestone = 0

    checking_changes = backend.read('checking_changes', default=[])
    gating_changes = backend.read('gating_changes', default=[])
    for change in gating_changes:
        change['gate'] = True

    # combine the two sets of changes
    changes = gating_changes + checking_changes
    changes = sorted(changes, key=lambda x: x['eta'])

    for change in changes:
        change['eta'] = utils.human_readable_duration(change['eta'])
        change['number'] = change['url'].split('/')[-1]
        change.setdefault('gate', False)

        review = gerrit.get_review(change['number'])
        if review is not None:
            change['subject'] = review['subject']
        else:
            change['subject'] = 'Unknown'

    d = dict(
        open_reviews=backend.read('open_reviews', default=0),
        gate_duration=utils.human_readable_duration(gate_duration),
        failed_merges=backend.read('failed_merges', default=0),
        next_milestone=utils.human_readable_duration(next_milestone),
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
