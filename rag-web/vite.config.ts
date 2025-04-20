import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';

// @ts-expect-error process is a nodejs global
const host = process.env.TAURI_DEV_HOST;

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 1420,
    strictPort: true,
    host: true,
  },
  clearScreen: false,
})
