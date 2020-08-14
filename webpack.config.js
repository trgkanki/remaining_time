const path = require('path')
const webpack = require('webpack')
const fs = require('fs')

function getAddonUUID () {
  return fs.readFileSync('src/UUID', { encoding: 'utf-8' }).trim()
}

module.exports = {
  entry: {
    main: './jssrc/index.ts'
  },
  output: {
    filename: 'main.min.js',
    path: path.resolve(__dirname, 'src/js'),
    libraryTarget: 'window',
    library: 'mainLib'
  },
  mode: process.env.NODE_ENV || 'production',
  devtool: 'source-map',
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: ['ts-loader']
      },
      {
        test: /\.scss$/,
        use: [
          'style-loader',
          'css-loader',
          'sass-loader'
        ]
      },
      {
        test: /\.css$/,
        use: [
          'style-loader',
          'css-loader'
        ]
      }
    ]
  },
  resolve: {
    modules: [
      'node_modules'
    ],
    extensions: ['.js', '.ts']
  },
  plugins: [
    new webpack.DefinePlugin({
      ADDON_UUID: JSON.stringify(getAddonUUID())
    })
  ]
}
