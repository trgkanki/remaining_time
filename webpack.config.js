const path = require('path')

module.exports = {
  entry: {
    main: './jssrc/index.ts'
  },
  output: {
    filename: 'main.min.js',
    path: path.resolve(__dirname, 'src'),
    libraryTarget: 'window',
    library: 'mainLib'
  },
  mode: 'production',
  devtool: 'source-map',
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: ['ts-loader']
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
