import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'
import './style.css'

// WhatsApp Desk uses a light theme throughout (like Whatomate / Polyg.in).
document.documentElement.dataset.theme = 'light'

createApp(App).use(router).mount('#app')
