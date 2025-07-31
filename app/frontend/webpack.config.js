import CopyPlugin from "copy-webpack-plugin";
// import ESLintPlugin from "eslint-webpack-plugin"
import HtmlWebpackPlugin from "html-webpack-plugin";
import MiniCssExtractPlugin from "mini-css-extract-plugin";
import path from "path";
import StylelintPlugin from "stylelint-webpack-plugin";
import { fileURLToPath } from "url";
import webpack from "webpack";
import { WebpackManifestPlugin } from "webpack-manifest-plugin";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default (env, argv) => ({
  mode: argv.mode,
  devtool: argv.mode === "development" ? "eval-cheap-source-map" : "source-map",
  context: path.resolve(__dirname),
  entry: ["./static/js/index.js", "./static/scss/main.css"],
  output: {
    path: path.resolve(__dirname, "webpack_assets/"),
    filename: "../config/static/js/bundled/[name].bundle.js",
    publicPath: "/static/", // Should match Django STATIC_URL
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        enforce: "pre",
        use: {
          loader: "source-map-loader",
          options: {
            filterSourceMappingUrl: (url, _resourcePath) => {
              if (/.+\.bundle\.js$/i.test(url)) {
                return "skip";
              }
              // or change to true to have 3rd party library sourcemaps included
              return false;
            },
          },
        },
      },
      {
        // Maybe should use type rather than test - https://webpack.js.org/plugins/mini-css-extract-plugin/#chunkfilename
        // says "Note that type should be used instead of test in Webpack 5, or else an extra .js file can be generated besides the .css file."
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, "css-loader", "postcss-loader"],
        exclude: [/node_modules/],
      },
      {
        test: /\.(jpg|jpeg|png|gif|webp|svg|mp4)(\?.*)?$/,
        type: "asset/resource",
        generator: {
          filename: (source) => source.filename.replace("static/", ""),
        },
      },
      {
        test: /\.(ttf|eot|woff|woff2)$/,
        type: "asset/resource",
        generator: {
          filename: (source) => source.filename.replace("static/", ""),
        },
      },
    ],
  },
  // optimization: {
  //   minimize: true,
  //   minimizer: [
  //     `...`,
  //     new CssMinimizerPlugin({
  //       test: /\.css$/,
  //     }),
  //   ],
  // },
  plugins: [
    // new webpack.DefinePlugin({
    //   SENTRY_RELEASE: JSON.stringify(process.env.SENTRY_RELEASE),
    // }),
    new MiniCssExtractPlugin({
      // path we want to write to relative to output path defined above, which is webpack_assets
      // filename: './static/css/[name].css',  <- in normal template I use now, but keeping with what has worked.
      filename: "./static/css/main.css", // where we want it to write relative to path above
    }),
    // new StylelintPlugin({
    //   context: path.resolve(__dirname),
    //   files: path.join('static/scss', '**/*.s?(a|c)ss'),
    //   configFile: path.join(path.resolve(__dirname), '.stylelintrc.json'),
    // }),
    // new ESLintPlugin({ extensions: ['js', 'ts'] }),
  ],
});
