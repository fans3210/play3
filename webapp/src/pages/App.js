import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import Uploader from '../components/Uploader';
import { initSocket } from '../utils/ws';
import DataVisualizer from '../components/DataVisualizer';

const App = () => {
    const dispatch = useDispatch();

    useEffect(() => {
        initSocket();
    }, []);




    return (
        <div style={{ padding: 40 }}>
            <div>Upload CSV File: </div>
            <Uploader />
            <DataVisualizer />
        </div>);
};

export default App;