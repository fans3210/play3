import pytest
import pandas as pd
# from pandas.testing import 
import util.data_processor as dp
import numpy as np
from app.errs import DataValidationError


def test_should_have_valid_cols():
    df = _gen_original_df(rename=True)
    assert dp._has_valid_columns(df)

def test_invalid_cols():
    df = _gen_original_df()
    df.rename(columns={'region': 'region2'}, inplace=True)
    assert not dp._has_valid_columns(df)

def test_unique_order_id():
    df = _gen_original_df(rename=True)
    assert len(dp._duplicate_order_ids(df)) == 0

def test_detect_duplicate_order_id():
    df = _gen_original_df(rename=True)
    df2 = _gen_original_df(rename=True)
    df3 = df.append(df2, ignore_index=True)
    assert len(dp._duplicate_order_ids(df3)) > 0

def test_should_remove_null_values():
    df = _gen_original_df()
    df2 = _gen_original_df()
    df3 = df.append(df2, ignore_index=True)

    df3['Region'][0] = np.nan
    df3.to_csv('tests/test_data/df3.csv', index=False)
    chunk = next(dp._read_n_process_csv_to_chunks('tests/test_data/df3.csv', chunk_size=100))
    df = dp._process_chunk(chunk)
    assert df.shape[0] == df3.shape[0] - 1

def test_valid_col_types():
    df = _gen_original_df(rename=True)
    valid, invalids = dp._has_valid_column_types(df)
    # assert valid
    print(invalids)
    print(df.dtypes)
    assert len(invalids) == 0
    
 
def test_invalid_col_types():
    df = _gen_original_df(rename=True)
    df['total_cost'][0] = 'abc'
    valid, _ = dp._has_valid_column_types(df)
    assert not valid


# helper funcs
def _gen_original_df(rename=False):
    cols = ['Region', 'Country', 'Item Type', 'Sales Channel', 'Order Priority', 'Order Date',
                 'Order ID', 'Ship Date', 'Units Sold', 'Unit Price', 'Unit Cost', 'Total Revenue', 'Total Cost', 'Total Profit', 'NRIC']

    data = {'Region': ['Sub-Saharan Africa'], 'Country': ['South Africa'], 'Item Type': ['Fruits'], 'Sales Channel': ['Offline'], 'Order Priority': ['L'],
    'Order Date': ['27/7/12'], 'Order ID': [443368995], 'Ship Date': ['28/7/12'], 'Units Sold': [9], 'Unit Price': [9.33], 'Unit Cost': [9.33], 
    'Total Revenue': [14862.69], 'Total Cost': [14862.69],
    'Total Profit': [3839.13], 'NRIC': ['T2076413D']
    }
    df = pd.DataFrame(columns=cols, data=data)
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    if rename:
        dp._rename_cols(df, inplace=True)
    return df

