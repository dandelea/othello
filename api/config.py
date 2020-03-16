import os

MONGO_USERNAME  = os.environ.get('MONGO_USERNAME') or 'root'
MONGO_PASSWORD  = os.environ.get('MONGO_PASSWORD') or 'password'
MONGO_HOSTNAME  = os.environ.get('MONGO_HOSTNAME') or 'localhost'
MONGO_PORT      = os.environ.get('MONGO_PORT') or 27017
