import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'

// The frappeui plugin handles the dev proxy, base URL, build output, and copying the entry
// HTML into the app's www/ with Jinja boot data injected. Our frontend/ is at the repo root
// (not a bench-app layout), so the plugin can't auto-detect paths — we pass them explicitly.
export default defineConfig({
  plugins: [
    frappeui({
      frontendRoute: '/whatsapp',
      buildConfig: {
        outDir: '../whatsapp_desk/public/frontend',
        indexHtmlPath: '../whatsapp_desk/www/whatsapp.html',
        baseUrl: '/assets/whatsapp_desk/frontend/',
      },
    }),
    vue(),
  ],
})
