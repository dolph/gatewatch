import os

import flask


app = flask.Flask(__name__)

# start with a default configuration
app.config.from_object('gatewatch.config')

# override defaults with custom configuration
conf_path = os.path.expanduser('gatewatch.conf.py')
app.config.from_pyfile(conf_path, silent=True)

# enable logging in production
if not app.debug:
    import logging
    file_handler = logging.FileHandler(app.config['LOG_FILE'])
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)


import gatewatch.views  # flake8: noqa
