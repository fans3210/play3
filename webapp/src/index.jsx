import React from 'react';
import ReactDOM from 'react-dom';
import App from './pages/App';
import { Provider } from 'react-redux';
import 'antd/dist/antd.css'; 

import { store } from './store';

ReactDOM.render(
    <Provider store={store}>
        <App />
    </Provider>
    ,
    document.querySelector('#app')
);