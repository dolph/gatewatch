import uuid


DEBUG = False
TESTING = False
LOG_FILE = '/tmp/gatewatch.log'

# if you don't override the secret key, one will be chosen for you
SECRET_KEY = uuid.uuid4().hex

# primary persistence
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 1

# put the task broker on a different DB
BROKER_URL = 'redis://%s:%s/%s' % (REDIS_HOST, REDIS_PORT, 0)
