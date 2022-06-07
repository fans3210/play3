import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { countData, retrieveData } from '../actions/dataActions';
import { Pagination, Table } from 'antd';
import { config } from '../configs';

const jsonKeys = [
    'order_id', 'region', 'country', 'item_type', 'sales_channel', 'order_priority', 'order_date',
    'ship_date', 'units_sold', 'unit_price', 'unit_cost', 'total_revenue', 'total_cost', 'total_profit',
    'nric'
];


const columns = jsonKeys.map(k => {
    return {
        title: toColName(k),
        dataIndex: k,
        key: k
    }
});


const DataVisualizer = () => {
    const [current, setCurrent] = useState(1);

    const dispatch = useDispatch();
    const total = useSelector(state => state.data.count);
    const batchData = useSelector(state => state.data.records);
    const uploadStatus = useSelector(state => state.data.upload);
    const progress = uploadStatus?.progress || 0;

    useEffect(() => {
        dispatch(countData());
        dispatch(retrieveData(config.PER_PAGE, (current - 1) * config.PER_PAGE));
    }, []);

    useEffect(() => {
        dispatch(retrieveData(config.PER_PAGE, (current - 1) * config.PER_PAGE));
    }, [current]);

    useEffect(() => {
        if (progress >= 100) {
            // refresh data display
            dispatch(countData());
            dispatch(retrieveData(config.PER_PAGE, (current - 1) * config.PER_PAGE));
        }
    }, [progress]);

    const onChange = page => {
        setCurrent(page);
    };



    return (
        <>
            {total} records in total
            {
                (total && total > 0 && batchData) &&
                <>
                    <Pagination
                        defaultCurrent={1}
                        total={total}
                        current={current}
                        onChange={onChange}
                        defaultPageSize={config.PER_PAGE}
                        pageSize={config.PER_PAGE}
                        showSizeChanger={false}
                        showQuickJumper
                    />
                    <Table
                        columns={columns}
                        dataSource={batchData}
                        pagination={false}
                        size='small'
                        rowKey='order_id'
                        scroll={{ y: 700 }}
                    />
                </>
            }

        </>
    );
};

function toColName(k) {
    const uppercaseWords = str => str.replace(/^(.)|\s+(.)/g, c => c.toUpperCase());

    if ('nric' === k) {
        return k.toUpperCase(); // nric case
    }

    const str = k.split('_').join(' ');
    return uppercaseWords(str);
};

export default DataVisualizer;