import CssMinimizerPlugin from "css-minimizer-webpack-plugin";
import ESLintPlugin from "eslint-webpack-plugin";
import MiniCssExtractPlugin from "mini-css-extract-plugin";
import path from "path";
import StylelintPlugin from "stylelint-webpack-plugin";
import { fileURLToPath } from "url";
import webpack from "webpack";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default (env, argv) => ({
  mode: argv.mode,
  devtool: argv.mode === "development" ? "eval-cheap-source-map" : "source-map",
  context: path.resolve(__dirname),
  entry: {
    index: "./static/js/index.js",
    // This unfortunately results in a main.bundle.js which is junk since this just an artifact
    // of how our plugins process css.
    // Pretty sure there is a way to configure webpack so that doesn't happen.
    main: "./static/scss/main.css",
  },
  output: {
    // webpack_assets/ output path is due to how webpack handles images, etc.
    // so that it does not overwrite the images already in static/img/, etc. See comments
    // at the asset/resource rules entries.
    path: path.resolve(__dirname, "webpack_assets/"),
    // filename: './static/js/bundled/index.bundle.js',
    // where we want it to write relative to path above or maybe we should use path.resolve here as well
    filename: "../static/js/bundled/[name].bundle.js",
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
      // These create copies of files which there is really no need to. See if we can find a way to not even copy
      // the files either by sym linking or just using them in place.
      // The old config used `asset/inline` for the images and `url-loader` for the fonts and images.
      // This resulted in inlining all of these which made for HUGE css files which were several MB in size.
      // This also specifies the filename so that webpack will not use the hashes. Django already
      // hashes these when we run collectstatic and updates the css files. We want the non-hashed
      // names so that we know what the real filenmes django sees will be so that we can preload them
      {
        test: /\.(jpg|jpeg|png|gif|webp|svg|mp4)(\?.*)?$/,
        type: "asset/resource",
        generator: {
          // filename: '[path][name][ext]',
          filename: (source) => source.filename.replace("static/", ""),
        },
      },
      {
        test: /\.(ttf|eot|woff|woff2)$/,
        type: "asset/resource",
        generator: {
          // filename: '[path][name][ext]',
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
      filename: "./static/css/[name].css",
    }),
    new StylelintPlugin({
      context: path.resolve(__dirname),
      files: path.join("static", "scss", "**/*.s?(a|c)ss"),
      configFile: path.join(path.resolve(__dirname), ".stylelintrc.json"),
    }),
    new ESLintPlugin({
      configType: "flat",
      extensions: ["js", "ts"],
    }),
  ],
});
