import flask


app = flask.Flask(__name__, instance_relative_config=True)

# start with a default configuration
app.config.from_object('gatewatch.config')

# override defaults with instance-specific configuration
app.config.from_pyfile('gatewatch_config.py', silent=True)


import gatewatch.views  # flake8: noqa
