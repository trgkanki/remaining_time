module.exports = {
  env: {
    browser: true,
    es6: true
  },
  overrides: [
    {
      files: ['*.js', '*.jsx'],
      extends: [
        'standard'
      ]
    },
    {
      files: ['*.ts', '*.tsx'],
      extends: [
        'eslint:recommended',
        'plugin:@typescript-eslint/eslint-recommended',
        'plugin:@typescript-eslint/recommended',
        'standard'
      ],
      rules: {
        // disable the rule for all files
        '@typescript-eslint/explicit-function-return-type': 'off',
        '@typescript-eslint/no-explicit-any': 'off',
        'no-undef': 'off'
      }
    }
  ],
  globals: {
    Atomics: 'readonly',
    SharedArrayBuffer: 'readonly'
  },
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2018,
    sourceType: 'module'
  },
  plugins: [
    '@typescript-eslint'
  ]
}
