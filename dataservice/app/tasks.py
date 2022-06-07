import os
import re
import time

import pandas as pd
import util.data_processor as data_processor
import util.mysql_ops as mysql_ops
import util.socket_ops as socket_ops
from config.config import (DATA_INSERT_UPDATE_END_PROGRESS,
                           DATA_INSERT_UPDATE_START_PROGRESS,
                           DATA_PROCESSING_END_PROGRESS,
                           DATA_PROCESSING_START_PROGRESS)
from flask_socketio import SocketIO, rooms

from app.app import clogger, cworker


@cworker.task(name='celery_tasks.analyze')
def analyze(msg_q, file_name, client_id):
    '''
    progress: 1%-10%
    '''
    skt = SocketIO(message_queue=msg_q)
    print('received filename = ', file_name)
    processed_file_path = data_processor.process(file_name, skt, client_id)

    return processed_file_path


@cworker.task(name='celery_tasks.save_to_db')
def insert_to_sql(processed_file_path, msg_q, client_id):
    '''
    progress: 20%-100%
    '''
    if not processed_file_path:
        # no data passed from chained task
        return
    skt = SocketIO(message_queue=msg_q)
    clogger.info('background task triggered')
    # df = pd.DataFrame.from_dict(df_as_dict).astype(
    #     {'ship_date': 'datetime64[ns]', 'order_date': 'datetime64[ns]'})

    # using different date parser since this is processed df
    df = pd.read_csv(processed_file_path, parse_dates=[
                     'order_date', 'ship_date'], date_parser=_simple_date_parser)
    print('df.info from task 2 = ', df.info())
    print(df.order_date.head())

    clogger.info('server emit task start')
    socket_ops.notify_client(skt, progress=DATA_INSERT_UPDATE_START_PROGRESS,
                             status='processing', room=client_id, details='Start inserting data')
    # skt.emit('my response', {"foo": "task starts"},
    #          namespace='/datasocket', room=client_id)
    try:
        affected = mysql_ops.update_insert_df(df, notifier=skt, room=client_id)    
        print('affected rows: ', affected)
        socket_ops.notify_client(skt, progress=DATA_INSERT_UPDATE_END_PROGRESS,
                                status='complete', room=client_id, details='{} rows affected'.format(affected))
        # skt.emit('my response', {"data": "task complete"},
        #          namespace='/datasocket', room=client_id)
        clogger.info(
            'server emit task complete, send to room: {}'.format(client_id))
    except Exception:
        socket_ops.notify_client(skt, progress=DATA_INSERT_UPDATE_START_PROGRESS,
                        status='error', room=client_id, details='insert to db failed, pls verify your data')


def _simple_date_parser(x):
    date = pd.to_datetime(
        x, format='%Y-%m-%d')
    return date
