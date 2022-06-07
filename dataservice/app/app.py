from celery import Celery
from celery.utils.log import get_task_logger
from config.socketio import DataNamespace
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from config.config import CELERY_BACKEND, CELERY_BROKER_URL, SOCKETIO_REDIS_URL
import util.api_helper as api_helper

app = Flask(__name__)
api_helper.register_errors(app)

CORS(app, support_credentials=True, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
socketio = SocketIO(app, cors_allowed_origins='*',
                    async_mode='eventlet', message_queue=SOCKETIO_REDIS_URL)
socketio.on_namespace(DataNamespace('/datasocket'))

cworker = Celery(app.name, broker=CELERY_BROKER_URL, backend=CELERY_BACKEND)
clogger = get_task_logger(app.name)
