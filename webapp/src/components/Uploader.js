import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { message, Progress, Typography } from 'antd';
import axios from 'axios';
import { config } from '../configs';
import { uploadDateProgress } from '../actions/dataActions';

const client = axios.create({
    baseURL: process.env.BASE_URL,
    timeout: 60000, // miliseconds
    headers: {
        "Content-Type": "application/json"
    }
});

const Uploader = () => {

    const dispatch = useDispatch();
    const uploadStatus = useSelector(state => state.data.upload);

    useEffect(() => {

    }, []);

    const uploadFile = async ({ target: { files } }) => {

        let data = new FormData();
        data.append('file', files[0]);

        const options = {
            onUploadProgress: (progressEvent) => {
                const { loaded, total } = progressEvent;
                let percent = Math.floor((loaded * 100) / total);
                percent = Math.min(config.FILE_UPLOAD_COMPLETION_PROGRESS, percent);
                dispatch(uploadDateProgress(percent, 'uploading...', 'processing'));
            },
            headers: {
                'clientId': localStorage.getItem('clientId')
            }
        };

        try {
            const res = await client.post(process.env.BASE_URL + '/api/data/upload', data, options);
            console.log(res.data);
        } catch (err) {
            message.error(err.response?.data?.message || 'failed');
            dispatch(uploadDateProgress(0, '', 'error'));
        }

    };

    const progress = uploadStatus?.progress || 0;
    const detail = uploadStatus?.detail || '';
    const status = uploadStatus?.status || 'complete';

    const { Text } = Typography;
    return (
        <>
            <input type='file' onChange={uploadFile} />
            <Progress percent={progress} />
            <div>
                <Text type={status === 'complete' ? 'success' : status === 'error' ? 'danger' : 'warning'} strong>
                    {detail}
                </Text>
            </div>
        </>
    );
};


export default Uploader;