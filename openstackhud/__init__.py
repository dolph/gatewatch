import flask


app = flask.Flask(__name__, instance_relative_config=True)

# start with a default configuration
app.config.from_object('openstackhud.config')

# override defaults with instance-specific configuration
app.config.from_pyfile('openstackhud_config.py', silent=True)


import openstackhud.views  # flake8: noqa
