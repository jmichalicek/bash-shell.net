import js from "@eslint/js"
import eslintConfigPrettier from "eslint-config-prettier"
import eslintPluginPrettierRecommended from "eslint-plugin-prettier/recommended"
import globals from "globals"

export default [
  {
    ignores: ["**/webpack.config.js", "**/static/js/bundled/"],
  },
  {
    languageOptions: {
      globals: {
        SENTRY_RELEASE: "readonly",
        ...globals.browser,
      },
    },
  },
  js.configs.recommended,
  eslintConfigPrettier,
  {
    rules: {
      "no-unused-vars": [
        "error",
        {
          vars: "all",
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
        },
      ],
      indent: ["error", 2],
      "comma-dangle": ["error", "always-multiline"],
    },
  },
  // docs say this should be last
  eslintPluginPrettierRecommended,
]
