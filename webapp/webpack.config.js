const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require('webpack');
const path = require('path');

module.exports = {
    entry: './src/index.jsx',
    output: {
        path: path.resolve(__dirname, 'dist/client'),
        filename: 'js/bundle.js',
    },
    devtool: 'inline-source-map',
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                loader: "babel-loader"
            },
            {
                test: /\.scss|css$/,
                use: ['style-loader', 'css-loader', 'sass-loader']
            }
        ]
    },

    resolve: {
        extensions: ['.js', 'jsx', '.css', '.sass']
    },
    devServer: {
        host: '0.0.0.0',
        port: 3000,
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './index.html'
        }),
        new webpack.DefinePlugin({
            'process.env.BASE_URL': JSON.stringify(process.env.BASE_URL),
        }),

    ]

};