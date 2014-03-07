import uuid


DEBUG = False
TESTING = False
LOG_FILE = '/tmp/gatewatch.log'

# if you don't override the secret key, one will be chosen for you
SECRET_KEY = uuid.uuid4().hex
