import os

import flask

from openstackhud import app  # flake8: noqa
from openstackhud import collect
from openstackhud import decorators


@app.route('/', methods=['GET'])
@decorators.templated()
def index():
    gate_duration = collect.get_gate_duration()
    return dict(
        gate_duration=collect.human_readable_duration(gate_duration))


@app.errorhandler(404)
def handle_not_found(error):
    return flask.render_template('not_found.html'), 404


@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/x-icon')
