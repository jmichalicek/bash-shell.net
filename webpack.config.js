const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const StylelintPlugin = require('stylelint-webpack-plugin');
const path = require('path');

var config = {
  mode: 'development',
  devtool: 'source-map',
  entry: [
    './app/config/static/js/index.js',
    './app/config/static/scss/main.scss',
  ],
  output: {
    path: path.resolve(__dirname , 'webpack_assets/'),
    // filename: './config/static/js/bundled/index.bundle.js',
    // where we want it to write relative to path above or maybe we should use path.resolve here as well
    filename: '../app/config/static/js/bundled/index.bundle.js',
    publicPath: "/static/", // Should match Django STATIC_URL
  },
  devServer: {
    writeToDisk: true, // Write files to disk in dev mode, so Django can serve the assets
  },
  module: {
    rules: [
      {
        test: /\.scss$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader', 'resolve-url-loader', 'sass-loader'],
      },
      {
        test: /\.css$/,
        loader: 'css-loader',
      },
      // These create copies of files which there is really no need to. Can't figure out how to
      // make these work without doing that, though. Possibly `asset/source` to leave as is.
      // The old config used `asset/inline` for the images and `url-loader` for the fonts.
      // This resulted in inlining all of these which made for HUGE css files, several MB in size.
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
      }

    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      // filename: './config/static/css/index.css',
      filename: '../app/config/static/css/main.css', // where we want it to write relative to path above
    }),
    // new StylelintPlugin({
    //   files: path.join('config/static/scss', '**/*.s?(a|c)ss'),
    // }),
  ],
  watch: true
};

module.exports = (env, argv) => {
  if (argv.mode === 'production') {
    config.watch = false;
  }
  return config;
}