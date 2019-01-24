module.exports = {
  devtool: 'cheap-module-eval-source-map',
  entry: {
    main: __dirname + '/dev/index.js'
  },
  output: {
    path: __dirname + '/public',
    filename: 'index.js',
    publicPath: '/public/'
  },
  module: {
    rules: [{
      test: /\.m?js$/,
      exclude: /(node_modules|bower_components)/,
      use: {
        loader: 'babel-loader',
        options: {
          presets: ['@babel/preset-env']
        }
      }
    }]
  }
}
