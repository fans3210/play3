import { RETRIEVE_DATA, COUNT_DATA, UPLOAD_DATA_PROGRESS } from '../actions/dataActions';
import moment from 'moment';

const initialState = {
    records: [],
    count: 0,
    upload: null,
};

const dataReducer = (state = initialState, action) => {
    switch (action.type) {
        case UPLOAD_DATA_PROGRESS:
            return {
                ...state,
                upload: action.payload
            };
        case RETRIEVE_DATA:
            const records = action.payload.data?.map(r => {
                const { order_date, ship_date, ...rest } = r;
                return {
                    ...rest,
                    order_date: moment(order_date).format('yyyy-MM-DD'),
                    ship_date: moment(ship_date).format('yyyy-MM-DD'),
                };
            });
            return {
                ...state,
                records,
            };
        case COUNT_DATA:
            return {
                ...state,
                count: action.payload.data.cnt
            }
    }
    return state;
};

export default dataReducer;