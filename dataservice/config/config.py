import os

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_BACKEND = os.getenv('CELERY_BACKEND')
SOCKETIO_REDIS_URL = os.getenv('SOCKETIO_REDIS_URL')

DATA_PROCESSING_START_PROGRESS = 0
DATA_PROCESSING_END_PROGRESS = 50
DATA_INSERT_UPDATE_START_PROGRESS = 51
DATA_INSERT_UPDATE_END_PROGRESS = 100


CSV_READING_CHUNK_SIZE = 5000
MYSQL_INSERT_BATCH_SIZE = 1000  # based on most sql clients default limit is 1000
