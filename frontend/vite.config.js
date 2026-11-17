import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // '@' maps to src/ so imports like '@/store/auth' work from any depth
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // forward all /api/* requests to the Flask backend during dev
      // avoids CORS issues and mirrors how dist files are served in production
      '/api': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true, // wipe dist before each rebuild to avoid stale chunks
  },
});
