const path = require('path')

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
  }
}
