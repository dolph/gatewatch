import flask


app = flask.Flask(__name__)

# start with a default configuration
app.config.from_object('gatewatch.config')

# override defaults with instance-specific configuration
app.config.from_pyfile('/etc/gatewatch/gatewatch.conf.py', silent=True)


import gatewatch.views  # flake8: noqa
