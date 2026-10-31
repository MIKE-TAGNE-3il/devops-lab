// Configuration d'ESLint (format "flat config", celui d'ESLint 9+), lue par "npm run lint".
import js from '@eslint/js'
import { defineConfig, globalIgnores } from 'eslint/config'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import globals from 'globals'

export default defineConfig([
  // dist/ = résultat du build (code minifié généré), inutile à analyser.
  globalIgnores(['dist']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      // Règles de base d'ESLint : variable non définie, doublons, code inatteignable...
      js.configs.recommended,
      // Règles des hooks React : ordre d'appel et dépendances de useEffect.
      reactHooks.configs.flat.recommended,
      // Vérifie qu'un fichier de composant reste compatible avec le rechargement à chaud de Vite.
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 'latest',
      // Le code tourne dans le navigateur : window, document, fetch... sont des variables connues.
      globals: globals.browser,
      parserOptions: {
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    rules: {
      // ESLint seul ne comprend pas que <App /> utilise l'import "App" : on ignore donc les
      // variables en majuscule (composants React) et celles qui commencent par "_".
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }],
    },
  },
])
