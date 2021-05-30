const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const StylelintPlugin = require('stylelint-webpack-plugin');
const path = require('path');

var config = {
  mode: 'development',
  entry: [
    './config/static/js/index.js',
    './config/static/scss/main.scss',
  ],
  output: {
    path: path.resolve(__dirname, 'webpack_assets/'),
    // filename: './config/static/js/bundled/index.bundle.js',
    // where we want it to write relative to path above or maybe we should use path.resolve here as well
    filename: '../config/static/js/bundled/index.bundle.js',
    publicPath: "/static/", // Should match Django STATIC_URL
  },
  module: {
    rules: [
      {
        test: /\.scss$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader', 'sass-loader'],
      },
      {
        test: /\.css$/,
        loader: 'css-loader',
      },
      // These create copies of files which there is really no need to. See if we can find a way to not even copy
      // the files either by sym linking or just using them in place.
      // The old config used `asset/inline` for the images and `url-loader` for the fonts and images.
      // This resulted in inlining all of these which made for HUGE css files which were several MB in size.
      // This also specifies the filename so that webpack will not use the hashes. Django already
      // hashes these when we run collectstatic and updates the css files. We want the non-hashed
      // names so that we know what the real filenmes django sees will be so that we can preload them
      {
        test: /\.(jpg|jpeg|png|gif|webp|svg|mp4)(\?.*)?$/,
        type: 'asset/resource',
        generator: {
          filename: '[name][ext]',
        },
      },
      {
        test: /\.(ttf|eot|woff|woff2)$/,
        type: 'asset/resource',
        generator: {
          filename: '[name][ext]',
        },
    ],
  },
  optimization: {
    minimize: true,
    minimizer: [
      new CssMinimizerPlugin({
        test: /\.css$/,
      }),
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: './config/static/css/main.css',
    }),
    new StylelintPlugin({
      files: path.join('config/static/scss', '**/*.s?(a|c)ss'),
    }),
  ],
  watch: true
};

module.exports = (env, argv) => {
  if (argv.mode === 'production') {
    config.watch = false;
  }
  return config;
}