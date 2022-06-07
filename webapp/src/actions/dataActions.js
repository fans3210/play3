import axios from 'axios';

// ACTION TYPES
export const RETRIEVE_DATA = 'data/retrieve';
export const COUNT_DATA = 'data/count';

export const UPLOAD_DATA_PROGRESS = 'data/upload/progress';

const client = axios.create({
    baseURL: process.env.BASE_URL,
    timeout: 10000, // miliseconds
    headers: {
        "Content-Type": "application/json"
    }
});

export const uploadDateProgress = (progress, detail, status) => dispatch => {
    // status: processing, complete, error
    dispatch({
        type: UPLOAD_DATA_PROGRESS,
        payload: {
            progress,
            detail,
            status
        }
    });
};

export const countData = () => async dispatch => {
    try {
        const res = await client.get('/api/data/count');
        dispatch({
            type: COUNT_DATA,
            payload: res?.data || 0
        })
    } catch (err) {
        console.error(err);
    }
};

export const retrieveData = (limit, offset) => async dispatch => {
    const params = {
        limit,
        offset,
    }
    // console.log('limit, offset = ', limit, offset);
    try {
        const res = await client.get('/api/data', { params });

        dispatch({
            type: RETRIEVE_DATA,
            payload: res?.data || []
        });
    } catch (err) {
        console.error(err);
    }
};