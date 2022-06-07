from unittest import mock
import pytest
from app.app import app
from unittest import mock
import json

@mock.patch('app.routes.mysql_ops.num_of_data', return_value=100)
def test_count_data_api(mocker):
    client = app.test_client()
    res = client.get('/api/data/count')
    assert res.status_code == 200

@mock.patch('app.routes.mysql_ops.retrieve_data', return_value={'foo': 'bar'})
def test_retrieve_data_api(mocker):
    client = app.test_client()
    res = client.get('/api/data')
    assert res.status_code == 200

def test_upload_without_header():
    client = app.test_client()
    res = client.post('/api/data/upload', 
        data={'file': open('tests/test_data/test.txt', 'rb')},
        content_type='multipart/form-data'
    )
    assert res.status_code == 401

def test_upload_non_csv():
    client = app.test_client()
    res = client.post('/api/data/upload', 
        data={'file': open('tests/test_data/test.txt', 'rb')},
        content_type='multipart/form-data',
        headers={'clientId': 'test'}
    )
    data = json.loads(res.data)
    print(data)
    assert res.status_code == 400 and data['message'] == 'invalid file name'