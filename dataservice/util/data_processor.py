import pandas as pd
import re
import rstr
from app.errs import DataValidationError
import numpy as np
import os
from datetime import datetime
from config.config import (DATA_PROCESSING_END_PROGRESS,
                           DATA_PROCESSING_START_PROGRESS,
                           CSV_READING_CHUNK_SIZE)
import util.socket_ops as socket_ops
import pandas.api.types as ptypes

COLS_TEMPLATE = ['Region', 'Country', 'Item Type', 'Sales Channel', 'Order Priority', 'Order Date',
                 'Order ID', 'Ship Date', 'Units Sold', 'Unit Price', 'Unit Cost', 'Total Revenue', 'Total Cost', 'Total Profit', 'NRIC']

NA_VALUES_TEMPLATE = [
    'N/A',
    'n/a',
    'N/a',
    'NA',
    'na',
    'NAN',
    'Nan',
    'nan',
    'NaN',
    'null',
    'Null',
    'Nil',
    'nil',
    '',
]

NRIC_REGEX = r'^[STFG]\d{7}[A-Z]$'


def process(file_name, skt, client_id):
    lines = sum(1 for _ in open('/data/original/{}'.format(file_name)))
    rows_count = lines - 1 # without header
    chunk_size = CSV_READING_CHUNK_SIZE
    chunks = _read_n_process_csv_to_chunks('/data/original/{}'.format(file_name), chunk_size)
    os.makedirs('/data/processed', exist_ok=True)
    processed_file_path = '/data/processed/{}'.format(file_name)
    if os.path.exists(processed_file_path):
        os.remove(processed_file_path)
    write_header = True
    acc = 0
    try:
        for chunk in chunks:
            df = _process_chunk(chunk)
            df.to_csv(processed_file_path, mode='a', header=write_header, index=False)
            write_header = False  # Update so later chunks don't write header
            # update progress
            acc += df.shape[0]
            process_progress_ratio = acc/rows_count
            progress = DATA_PROCESSING_START_PROGRESS + (DATA_PROCESSING_END_PROGRESS - DATA_PROCESSING_START_PROGRESS) * process_progress_ratio
            print('process file progress: ===> {}'.format(progress))
            socket_ops.notify_client(skt, progress=progress, status='processing',
                                room=client_id, details='Analyzing & cleaning data in batches...')
        return processed_file_path
    except DataValidationError as e:
        socket_ops.notify_client(skt, progress=0, status='error', room=client_id, details=e.msg)
        return None

def _read_n_process_csv_to_chunks(file_path, chunk_size):
    chunks = pd.read_csv((file_path),
                    keep_default_na=False, na_values=NA_VALUES_TEMPLATE,
                    parse_dates=['Order Date', 'Ship Date'],
                    date_parser=_date_parser, cache_dates=True, chunksize=chunk_size)
    return chunks

def _process_chunk(chunk):
    df = chunk
    # pre-processing, drop nulls and white spaces for some columns
    df.replace(r'^\s*$', np.nan, regex=True,
            inplace=True)  # clean up white spaces to make it detected as null
    df.dropna(inplace=True)

    # add nric column
    df['NRIC'] = np.nan
    df['NRIC'] = df['NRIC'].apply(lambda _: _gen_valid_str(regex=NRIC_REGEX))

    _rename_cols(df, inplace=True)

    if not _has_valid_columns(df):
        raise DataValidationError(
            'invalid columns, make sure columns follow the template of {} and have correct types'.format(COLS_TEMPLATE))

    # print('df dtypes = ', df.dtypes)
    # print('first row = ', df.loc[0])
    has_valid_col_types, invalids = _has_valid_column_types(df)
    if not has_valid_col_types:
        raise DataValidationError('invalid column types {}'.format(invalids))

    duplicates = _duplicate_order_ids(df)
    if len(duplicates) > 0:
        raise DataValidationError(
            'orders have duplicate ids {}'.format(duplicates))

    return df

def _date_parser(x):
    date = pd.to_datetime(
        x, infer_datetime_format=True)
    return date


def _rename_cols(df, inplace=False):
    def _col_name_to_snake(col_name):
        name = ''.join(col_name.split(' '))
        pt1 = re.compile(r'(.)([A-Z][a-z]+)')
        pt2 = re.compile(r'([a-z0-9])([A-Z])')
        name = pt1.sub(r'\1_\2', name)
        return pt2.sub(r'\1_\2', name).lower()
    col_maps = {col: _col_name_to_snake(col) for col in COLS_TEMPLATE}
    df.rename(columns=col_maps, inplace=inplace)
    return df


def _has_valid_columns(df):
    cols = set(df.columns)
    snake_cols = set(['region', 'country', 'item_type', 'sales_channel', 'order_priority', 'order_date', 'order_id',
                      'ship_date', 'units_sold', 'unit_price', 'unit_cost', 'total_revenue', 'total_cost', 'total_profit', 'nric'])
    return snake_cols == cols

def _has_valid_column_types(df):
    region = ptypes.is_string_dtype(df.region)
    country = ptypes.is_string_dtype(df.country)
    item_type = ptypes.is_string_dtype(df.item_type)
    sales_channel = ptypes.is_string_dtype(df.sales_channel)
    order_priority = ptypes.is_string_dtype(df.order_priority)
    order_date = ptypes.is_datetime64_ns_dtype(df.order_date)
    order_id = ptypes.is_int64_dtype(df.order_id)
    ship_date = ptypes.is_datetime64_ns_dtype(df.ship_date)
    units_sold = ptypes.is_integer_dtype(df.units_sold)
    unit_price = ptypes.is_float_dtype(df.unit_price)
    unit_cost = ptypes.is_float_dtype(df.unit_cost)
    total_revenue = ptypes.is_float_dtype(df.total_revenue)
    total_cost = ptypes.is_float_dtype(df.total_cost)
    total_profit = ptypes.is_float_dtype(df.total_profit)
    nric = ptypes.is_string_dtype(df.nric)

    arr = [region, country, item_type, sales_channel, order_priority, order_date, order_id, ship_date, units_sold, unit_price, unit_cost,
    total_revenue, total_cost, total_profit, nric]
    invalids = [ele for (idx, ele) in enumerate(COLS_TEMPLATE) if not arr[idx]]

    return not invalids, invalids


def _duplicate_order_ids(df):
    duplicates = list(df.order_id[df.duplicated(subset=['order_id']) == True])
    return duplicates


def _gen_valid_str(regex):
    return rstr.xeger(regex)
