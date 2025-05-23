import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' // 🆕

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())

  return {
    plugins: [vue()],
    define: {
      'process.env': env,
      'import.meta.env.VUE_APP_API_URL': JSON.stringify(env.VUE_APP_API_URL || 'https://diplomatch-tiizx.kinsta.app'),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'), // 🆕 Добавляем алиас "@"
      },
    },
  }
})
