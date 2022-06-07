import util.mysql_ops as mysql_ops
from util.api_helper import make_res
from flask import jsonify
from flask.globals import request
from werkzeug.exceptions import RequestEntityTooLarge
from celery import chain
import os
from app.app import app
from app.tasks import insert_to_sql, analyze
from config.config import SOCKETIO_REDIS_URL
from app.errs import ApiError


@app.route(f'/api/data/count', methods=['GET'])
def count_data():
    result = mysql_ops.num_of_data()
    res = make_res(200, payload=result)
    return res


@app.route(f'/api/data', methods=['GET'])
def retrieve_data():
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    results = mysql_ops.retrieve_data(limit, offset)
    res = make_res(200, payload=results)
    return res


@app.route(f'/api/data/upload', methods=['POST'])
def upload_csv():
    client_id = request.headers.get('clientId')
    if not client_id:
        raise ApiError(401, 'please check your socket connection')
    try:
        if 'file' not in request.files:
            raise ApiError(400, 'no file part')

        file = request.files['file']
        if not file or file.filename == '':
            raise ApiError(400, 'no selected file')

        if not _allowed_file(file.filename):
            raise ApiError(400, 'invalid file name')

        os.makedirs('/data/original', exist_ok=True)
        file.save('/data/original/{}'.format(file.filename))

        # analyze.delay(SOCKETIO_REDIS_URL, file.filename)
        bg_task = chain(
            analyze.s(msg_q=SOCKETIO_REDIS_URL,
                      file_name=file.filename, client_id=client_id),
            insert_to_sql.s(msg_q=SOCKETIO_REDIS_URL, client_id=client_id)
        ).apply_async()
        print('bg_task.id = ', bg_task.id)
        return make_res(200, 'file received')
    except RequestEntityTooLarge:
        raise ApiError(413, 'file too large')


def _allowed_file(filename):
    allowed_exts = 'csv'
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_exts
