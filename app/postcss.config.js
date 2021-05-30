module.exports = {
    plugins: {
      autoprefixer: {},
      "postcss-pxtorem": {
        propList: ['font', 'font-size', 'line-height', 'letter-spacing', 'margin*', "padding*", "*width", "*height", "grid-template*"]
      }
    }
};