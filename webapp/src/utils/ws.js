import io from 'socket.io-client';
import { v4 as uuidv4 } from 'uuid';
import { config } from '../configs';
import { uploadDateProgress } from '../actions/dataActions';
import { store } from '../store';

let socket;

const { DATA_INGESTION_START_PROGRESS, DATA_INGESTION_COMPLETION_PROGRESS } = config;

export const initSocket = () => {
    console.log('init socket called');
    let clientId = localStorage.getItem('clientId');

    if (!clientId) {
        clientId = uuidv4();
        localStorage.setItem('clientId', clientId);
    }

    socket = io(`${process.env.BASE_URL}/datasocket`, {
        reconnection: true,
        reconnectionAttempts: 10,
        transports: ['websocket']
    });

    socket.connect().on('connect', () => {
        console.log(socket);
        console.log('socket id = ', socket.id);
        socket.emit('join', clientId);

        socket.on('joined room', msg => {
            console.log('received joined room event: ', msg);
        });

        socket.on('data_status', msg => {
            // console.log('datastatus:', msg);
            const { progress, details, status } = msg;
            const overallProgress = DATA_INGESTION_START_PROGRESS + (DATA_INGESTION_COMPLETION_PROGRESS - DATA_INGESTION_START_PROGRESS) / 100 * progress;
            store.dispatch(uploadDateProgress(overallProgress, details, status));
        });
    });
};